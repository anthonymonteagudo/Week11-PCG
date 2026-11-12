#include "TrailBiomeAuthoringLibrary.h"
#include "Modules/ModuleManager.h"
#include "PCGGraph.h"
#include "PCGNode.h"
#include "Elements/PCGMatchAndSetAttributes.h"
#include "StructUtils/PropertyBag.h"
#include "Engine/DataTable.h"
#include "Engine/StaticMesh.h"
#include "Engine/UserDefinedStruct.h"
#include "Kismet2/StructureEditorUtils.h"
#include "UserDefinedStructure/UserDefinedStructEditorData.h"
#include "EdGraphSchema_K2.h"
#include "UObject/StructOnScope.h"
#include "UObject/UnrealType.h"
#include "Engine/Texture2D.h"
#include "ImageCore.h"
#include "Interfaces/ITargetPlatformManagerModule.h"
IMPLEMENT_MODULE(FDefaultModuleImpl, TrailBiomeAuthoring)

bool UTrailBiomeAuthoringLibrary::DownsizeTeachingTexture(UTexture2D* Texture,int32 MaxDimension)
{
#if WITH_EDITOR
    if (!Texture || MaxDimension<256 || Texture->Source.GetNumLayers()!=1 || Texture->Source.GetNumBlocks()!=1) return false;
    FImage Image;
    if (!Texture->Source.GetMipImage(Image,0)) return false;
    if (Image.SizeX<=MaxDimension && Image.SizeY<=MaxDimension) return true;
    bool Changed=false;
    if (!Texture->DownsizeImageUsingTextureSettings(GetTargetPlatformManagerRef().GetRunningTargetPlatform(),Image,MaxDimension,0,Changed)) return false;
    if (Changed)
    {
        Texture->Modify();Texture->PreEditChange(nullptr);Texture->Source.Init(FImageView(Image));
        Texture->bUseLegacyGamma=false;Texture->PostEditChange();Texture->MarkPackageDirty();
    }
    return true;
#else
    return false;
#endif
}

void UTrailBiomeAuthoringLibrary::CommentNode(UPCGNode* Node, const FString& Comment)
{
#if WITH_EDITORONLY_DATA
    if (!Node) return;
    Node->Modify();Node->NodeComment=Comment;Node->bCommentBubblePinned=true;Node->bCommentBubbleVisible=true;Node->MarkPackageDirty();
#endif
}

void UTrailBiomeAuthoringLibrary::AddMuseumProfileParameters(UPCGGraph* Graph)
{
    if (!Graph) return;
    TArray<FPropertyBagPropertyDesc> D;
    D.Emplace(FName(TEXT("AssetSet")), EPropertyBagPropertyType::Object, UDataTable::StaticClass());
    D.Last().SetMetaData(TEXT("ToolTip"), TEXT("Compatible Mesh and Weight rows. The placement rules stay shared."));
    D.Emplace(FName(TEXT("VariationSeed")), EPropertyBagPropertyType::Int32);
    Graph->AddUserParameters(D);
    Graph->UpdateUserParametersStruct([](FInstancedPropertyBag& B) { B.SetValueInt32(TEXT("VariationSeed"),17); });
    Graph->MarkPackageDirty();
}

void UTrailBiomeAuthoringLibrary::AddBuildingParameters(UPCGGraph* Graph)
{
    if (!Graph) return;
    TArray<FPropertyBagPropertyDesc> D;
    D.Emplace(FName(TEXT("Cells")), EPropertyBagPropertyType::Struct, TBaseStructure<FVector>::Get());
    D.Last().SetMetaData(TEXT("DisplayName"), TEXT("Cells: X rows, Y columns, Z floors"));
    D.Last().SetMetaData(TEXT("ToolTip"), TEXT("Whole module counts. The graph floors values and clamps each axis to 1..12. This kit uses 400 cm bays and 350 cm storeys. Actor scale should remain 1."));
    D.Emplace(FName(TEXT("FacadeSet")), EPropertyBagPropertyType::Object, UDataTable::StaticClass());
    D.Last().SetMetaData(TEXT("ToolTip"), TEXT("Mesh/weight profile. Replacement meshes must share the measured wall dimensions, pivot and axes."));
    D.Emplace(FName(TEXT("VariationSeed")), EPropertyBagPropertyType::Int32);
    Graph->AddUserParameters(D);
    Graph->UpdateUserParametersStruct([](FInstancedPropertyBag& B) { B.SetValueInt32(TEXT("VariationSeed"), 17); });
    Graph->MarkPackageDirty();
}

void UTrailBiomeAuthoringLibrary::AddCompositionParameters(UPCGGraph* Graph)
{
    if (!Graph) return;
    TArray<FPropertyBagPropertyDesc> D;
    for (const auto& Name : {TEXT("HabitatTag"),TEXT("ClearingTag")})
    {
        FPropertyBagPropertyDesc P(FName(Name),EPropertyBagPropertyType::Name);
        P.SetMetaData(TEXT("DisplayName"), Name==FString(TEXT("HabitatTag")) ? TEXT("Closed habitat regions tag") : TEXT("Closed clearings tag"));
        P.SetMetaData(TEXT("ToolTip"),TEXT("Select all closed spline actors with this tag. Inclusion regions are unioned; clearings and the protected trail are subtracted."));D.Add(P);
    }
    Graph->AddUserParameters(D);
    Graph->UpdateUserParametersStruct([](FInstancedPropertyBag& B){B.SetValueName(TEXT("HabitatTag"),TEXT("Habitat_Grove"));B.SetValueName(TEXT("ClearingTag"),TEXT("Habitat_Clearing"));});Graph->MarkPackageDirty();
}

void UTrailBiomeAuthoringLibrary::AddHabitatControl(UPCGGraph* Graph)
{
    if (!Graph) return;
    FPropertyBagPropertyDesc P(FName(TEXT("FavorClearings")),EPropertyBagPropertyType::Bool);
    P.SetMetaData(TEXT("DisplayName"),TEXT("Favor habitat clearings"));
    P.SetMetaData(TEXT("ToolTip"),TEXT("Invert the shared patch mask. Useful for exposed rocks among less vegetated gaps."));
    Graph->AddUserParameters({P});Graph->UpdateUserParametersStruct([](FInstancedPropertyBag& B){B.SetValueBool(TEXT("FavorClearings"),false);});Graph->MarkPackageDirty();
}

void UTrailBiomeAuthoringLibrary::AddNaturalParameters(UPCGGraph* Graph)
{
    if (!Graph) return;
    TArray<FPropertyBagPropertyDesc> D;
    auto Add=[&](const TCHAR* Name,const TCHAR* Display,const TCHAR* Min,const TCHAR* Max,const TCHAR* Tip)
    {
        FPropertyBagPropertyDesc P(FName(Name),EPropertyBagPropertyType::Double);
        P.SetMetaData(TEXT("DisplayName"),Display);P.SetMetaData(TEXT("ClampMin"),Min);P.SetMetaData(TEXT("ClampMax"),Max);P.SetMetaData(TEXT("ToolTip"),Tip);D.Add(P);
    };
    Add(TEXT("PatchCutoff"),TEXT("Patch cutoff"),TEXT("0"),TEXT("0.8"),TEXT("Keep only the denser parts of a shared 50 m spatial noise field. Higher values open larger clearings. Zero disables patch rejection."));
    Add(TEXT("KeepFraction"),TEXT("Candidate survival fraction"),TEXT("0.2"),TEXT("1"),TEXT("Randomly thin eligible points under the variation seed. This is an expected fraction, not an exact final count."));
    Add(TEXT("SlopeMinDot"),TEXT("Ground flatness cutoff"),TEXT("0"),TEXT("1"),TEXT("Minimum dot product with world up. 0.94 is about 20 degrees. Normals are read before restoring upright tree rotations."));
    Add(TEXT("PruneRadiusCm"),TEXT("Pruning neighborhood (cm)"),TEXT("0"),TEXT("500"),TEXT("Scale the unit point bounds before randomized Self Pruning. This is a point influence radius, not full mesh collision clearance."));
    Graph->AddUserParameters(D);
    Graph->UpdateUserParametersStruct([](FInstancedPropertyBag& B)
    {
        B.SetValueDouble(TEXT("PatchCutoff"),0.4);B.SetValueDouble(TEXT("KeepFraction"),0.85);
        B.SetValueDouble(TEXT("SlopeMinDot"),0.94);B.SetValueDouble(TEXT("PruneRadiusCm"),180.0);
    });
    Graph->MarkPackageDirty();
}

FString UTrailBiomeAuthoringLibrary::ConfigureWeightSelector(UPCGGraph* Graph)
{
    if (!Graph) return TEXT("Missing graph");
    for (UPCGNode* Node : Graph->GetNodes())
    {
        if (auto* S=Cast<UPCGMatchAndSetAttributesSettings>(Node->GetSettings()))
        {
            S->Modify(); S->WeightAttribute.SetAttributeName(TEXT("Weight"));
            Graph->MarkPackageDirty();
            return S->WeightAttribute.ToString();
        }
    }
    return TEXT("Missing selector");
}

void UTrailBiomeAuthoringLibrary::AddBiomeParameters(UPCGGraph* Graph)
{
    if (!Graph) return;
    TArray<FPropertyBagPropertyDesc> D;
    auto Number = [&D](const TCHAR* Name, const TCHAR* Display, const TCHAR* Min, const TCHAR* Max, const TCHAR* Tip)
    {
        FPropertyBagPropertyDesc P(FName(Name), EPropertyBagPropertyType::Double);
        P.SetMetaData(TEXT("DisplayName"), Display);
        P.SetMetaData(TEXT("ClampMin"), Min); P.SetMetaData(TEXT("ClampMax"), Max);
        P.SetMetaData(TEXT("UIMin"), Min); P.SetMetaData(TEXT("UIMax"), Max);
        P.SetMetaData(TEXT("ToolTip"), Tip); D.Add(P);
    };
    Number(TEXT("SpacingCm"), TEXT("Candidate spacing (cm)"), TEXT("300"), TEXT("2400"), TEXT("Grid cell spacing. Lower values propose more points; this is not guaranteed final mesh separation."));
    Number(TEXT("ScaleMin"), TEXT("Uniform scale minimum"), TEXT("0.2"), TEXT("1.2"), TEXT("Lower end of the prepared uniform scale range. Keep this at or below ScaleMax."));
    Number(TEXT("ScaleMax"), TEXT("Uniform scale maximum"), TEXT("0.2"), TEXT("1.2"), TEXT("Upper end of the prepared uniform scale range. Recheck final clearance if asset bounds change."));
    D.Emplace(FName(TEXT("VariationSeed")), EPropertyBagPropertyType::Int32);
    D.Last().SetMetaData(TEXT("DisplayName"), TEXT("Variation seed"));
    D.Last().SetMetaData(TEXT("ToolTip"), TEXT("Select a repeatable variation for this graph instance under fixed conditions."));
    D.Emplace(FName(TEXT("AssetSet")), EPropertyBagPropertyType::Object, UDataTable::StaticClass());
    D.Last().SetMetaData(TEXT("DisplayName"), TEXT("Mesh and weight table"));
    D.Last().SetMetaData(TEXT("ToolTip"), TEXT("Native editable DataTable containing Mesh, Weight and FootprintRadiusCm rows."));
    D.Emplace(FName(TEXT("ReservationTag")), EPropertyBagPropertyType::Name);
    D.Last().SetMetaData(TEXT("DisplayName"), TEXT("Trail reservation tag"));
    D.Last().SetMetaData(TEXT("ToolTip"), TEXT("Prepared closed exclusion input. Keep the tag compatible with the chosen mesh set and maximum scale."));
    Graph->AddUserParameters(D);
    Graph->UpdateUserParametersStruct([](FInstancedPropertyBag& B)
    {
        B.SetValueDouble(TEXT("SpacingCm"), 900.0);
        B.SetValueDouble(TEXT("ScaleMin"), 0.8);
        B.SetValueDouble(TEXT("ScaleMax"), 1.2);
        B.SetValueInt32(TEXT("VariationSeed"), 17);
        B.SetValueName(TEXT("ReservationTag"), TEXT("Reserve_Trees"));
    });
    Graph->MarkPackageDirty();
}

bool UTrailBiomeAuthoringLibrary::ConfigureMeshTableStruct(UUserDefinedStruct* Struct)
{
    if (!Struct) return false;
    const auto Old = FStructureEditorUtils::GetVarDesc(Struct);
    auto Add = [Struct](const TCHAR* Name, const FEdGraphPinType& Type)
    {
        if (!FStructureEditorUtils::AddVariable(Struct, Type)) return false;
        const auto Id = FStructureEditorUtils::GetVarDesc(Struct).Last().VarGuid;
        return FStructureEditorUtils::RenameVariable(Struct, Id, Name);
    };
    FEdGraphPinType Mesh; Mesh.PinCategory=UEdGraphSchema_K2::PC_SoftObject;
    Mesh.PinSubCategoryObject=UStaticMesh::StaticClass();
    FEdGraphPinType Num; Num.PinCategory=UEdGraphSchema_K2::PC_Real; Num.PinSubCategory=UEdGraphSchema_K2::PC_Double;
    if (!Add(TEXT("Mesh"),Mesh) || !Add(TEXT("Weight"),Num) || !Add(TEXT("FootprintRadiusCm"),Num)) return false;
    for (const auto& V : Old) FStructureEditorUtils::RemoveVariable(Struct,V.VarGuid);
    Struct->MarkPackageDirty(); return true;
}

bool UTrailBiomeAuthoringLibrary::FillMeshTable(UDataTable* Table,const TArray<UStaticMesh*>& Meshes,const TArray<double>& Weights)
{
    if (!Table || !Table->GetRowStruct() || Meshes.Num()!=Weights.Num()) return false;
    const UScriptStruct* S=Table->GetRowStruct();
    FSoftObjectProperty* MP=nullptr; FDoubleProperty* WP=nullptr; FDoubleProperty* RP=nullptr;
    for (TFieldIterator<FProperty> It(S); It; ++It)
    {
        FString Name=S->GetAuthoredNameForField(*It);
        if (Name==TEXT("Mesh")) MP=CastField<FSoftObjectProperty>(*It);
        if (Name==TEXT("Weight")) WP=CastField<FDoubleProperty>(*It);
        if (Name==TEXT("FootprintRadiusCm")) RP=CastField<FDoubleProperty>(*It);
    }
    if (!MP || !WP || !RP) return false;
    Table->EmptyTable();
    for (int32 I=0; I<Meshes.Num(); ++I)
    {
        UStaticMesh* M=Meshes[I]; if (!M || Weights[I]<=0) return false;
        FStructOnScope Row(S);
        MP->SetPropertyValue_InContainer(Row.GetStructMemory(), FSoftObjectPtr(M));
        WP->SetPropertyValue_InContainer(Row.GetStructMemory(),Weights[I]);
        const auto B=M->GetBounds();
        const double Radius=FMath::Sqrt(FMath::Square(FMath::Abs(B.Origin.X)+B.BoxExtent.X)+FMath::Square(FMath::Abs(B.Origin.Y)+B.BoxExtent.Y));
        RP->SetPropertyValue_InContainer(Row.GetStructMemory(),Radius);
        Table->AddRow(FName(*FString::Printf(TEXT("Entry_%02d"),I+1)),*reinterpret_cast<FTableRowBase*>(Row.GetStructMemory()));
    }
    Table->MarkPackageDirty(); return true;
}
