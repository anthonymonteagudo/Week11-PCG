using UnrealBuildTool;
public class TrailBiomeAuthoring : ModuleRules
{
    public TrailBiomeAuthoring(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
        PublicDependencyModuleNames.AddRange(new [] { "Core", "CoreUObject", "Engine", "PCG" });
        PrivateDependencyModuleNames.AddRange(new [] { "UnrealEd", "BlueprintGraph", "AssetRegistry", "ImageCore", "TargetPlatform" });
    }
}
