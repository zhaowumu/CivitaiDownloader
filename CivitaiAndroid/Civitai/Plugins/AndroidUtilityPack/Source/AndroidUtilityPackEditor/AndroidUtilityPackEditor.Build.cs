// Copyright Porret Gaming 2024, All Rights Reserved

using UnrealBuildTool;

public class AndroidUtilityPackEditor : ModuleRules
{
	public AndroidUtilityPackEditor(ReadOnlyTargetRules Target) : base(Target)
	{
		PrivateDependencyModuleNames.AddRange(
			new string[] {
                "Core",
                "InputCore",
				"Engine",
				"Slate",
				"SlateCore",
				"EditorStyle",
				"PropertyEditor",
				"SharedSettingsWidgets",
				"UnrealEd",
                "CoreUObject"
            }
		);
	}
}
