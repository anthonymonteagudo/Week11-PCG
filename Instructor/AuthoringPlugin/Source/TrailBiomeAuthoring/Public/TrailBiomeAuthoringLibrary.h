#pragma once
#include "Kismet/BlueprintFunctionLibrary.h"
#include "TrailBiomeAuthoringLibrary.generated.h"
class UPCGGraph;
class UUserDefinedStruct;
class UDataTable;
class UStaticMesh;
class UPCGNode;
class UTexture2D;
UCLASS()
class TRAILBIOMEAUTHORING_API UTrailBiomeAuthoringLibrary : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()
public:
    UFUNCTION(BlueprintCallable, Category="Trail Authoring")
    static bool DownsizeTeachingTexture(UTexture2D* Texture, int32 MaxDimension);
    UFUNCTION(BlueprintCallable, Category="Trail Authoring")
    static void CommentNode(UPCGNode* Node, const FString& Comment);
    UFUNCTION(BlueprintCallable, Category="Trail Authoring")
    static void AddMuseumProfileParameters(UPCGGraph* Graph);
    UFUNCTION(BlueprintCallable, Category="Trail Authoring")
    static void AddBuildingParameters(UPCGGraph* Graph);
    UFUNCTION(BlueprintCallable, Category="Trail Authoring")
    static void AddBiomeParameters(UPCGGraph* Graph);
    UFUNCTION(BlueprintCallable, Category="Trail Authoring")
    static void AddNaturalParameters(UPCGGraph* Graph);
    UFUNCTION(BlueprintCallable, Category="Trail Authoring")
    static void AddHabitatControl(UPCGGraph* Graph);
    UFUNCTION(BlueprintCallable, Category="Trail Authoring")
    static void AddCompositionParameters(UPCGGraph* Graph);
    UFUNCTION(BlueprintCallable, Category="Trail Authoring")
    static bool ConfigureMeshTableStruct(UUserDefinedStruct* Struct);
    UFUNCTION(BlueprintCallable, Category="Trail Authoring")
    static bool FillMeshTable(UDataTable* Table, const TArray<UStaticMesh*>& Meshes, const TArray<double>& Weights);
    UFUNCTION(BlueprintCallable, Category="Trail Authoring")
    static FString ConfigureWeightSelector(UPCGGraph* Graph);
};
