import os
from manim import *
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.gtts import GTTSService
from rdkit import Chem
from rdkit.Chem import rdDepictor
from rdkit.Chem.Draw import MolDraw2DSVG


class DrugInteraction(VoiceoverScene):
    def construct(self):
        self.set_speech_service(GTTSService())

        # Introduction
        title = Text("Understanding Drug Interactions:", font_size=48).to_edge(UP, buff=0.5)
        subtitle = Text("Warfarin & Aspirin", font_size=42, color=YELLOW).next_to(title, DOWN)
        
        with self.voiceover(text="Let's explore the important interaction between two common blood-thinning medications: Warfarin and Aspirin."):
            self.play(Write(title), Write(subtitle))
            self.wait(1)

        # Individual Drug Explanations
        warfarin_smiles = "CC(=O)C(C1=CC=CC=C1)C2=CC(=O)OC=C2O"
        aspirin_smiles = "CC(=O)OC1=CC=CC=C1C(=O)O"
        
        warfarin_svg = SVGMobject("warfarin.svg").scale(0.7).move_to(LEFT * 3)
        aspirin_svg = SVGMobject("aspirin.svg").scale(0.7).move_to(RIGHT * 3)

        # Create info boxes for each drug
        warfarin_info = VGroup(
            Text("Warfarin", font_size=36, color=RED),
            Text("• Anticoagulant", font_size=24),
            Text("• Prevents blood clots", font_size=24),
            Text("• Blocks Vitamin K", font_size=24)
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2)

        aspirin_info = VGroup(
            Text("Aspirin", font_size=36, color=BLUE),
            Text("• Anti-platelet", font_size=24),
            Text("• Reduces inflammation", font_size=24),
            Text("• Inhibits platelets", font_size=24)
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2)

        # Create groups for each drug
        warfarin_group = VGroup(warfarin_svg, warfarin_info).arrange(DOWN, buff=0.5)
        aspirin_group = VGroup(aspirin_svg, aspirin_info).arrange(DOWN, buff=0.5)

        # Position the groups
        warfarin_group.to_edge(LEFT, buff=1)
        aspirin_group.to_edge(RIGHT, buff=1)

        with self.voiceover(text="Warfarin is a powerful anticoagulant that works by blocking Vitamin K, preventing blood clots from forming."):
            self.play(FadeOut(subtitle))
            self.play(FadeIn(warfarin_group))
            self.wait(1)

        with self.voiceover(text="Aspirin, on the other hand, works by inhibiting platelets, which are crucial for blood clotting."):
            self.play(FadeIn(aspirin_group))
            self.wait(1)

        # Blood vessel demonstration
        vessel = RoundedRectangle(height=1, width=6, corner_radius=0.5, fill_opacity=0.2, color=RED)
        vessel.move_to(DOWN * 2)
        blood_cells = VGroup(*[Circle(radius=0.1, fill_opacity=1, color=RED) for _ in range(6)])
        for i, cell in enumerate(blood_cells):
            cell.move_to(vessel.get_left() + RIGHT * (i + 0.5))

        with self.voiceover(text="When these medications are combined, they affect blood clotting in different ways:"):
            self.play(Create(vessel), FadeIn(blood_cells))
            self.wait(1)

        # Show interaction effects
        effect_text = VGroup(
            Text("Combined Effects:", font_size=36, color=YELLOW),
            Text("1. Enhanced bleeding risk", font_size=28),
            Text("2. Longer bleeding time", font_size=28),
            Text("3. Higher risk of internal bleeding", font_size=28),
            Text("4. Increased bruising", font_size=28)
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        effect_text.next_to(vessel, DOWN, buff=0.5)

        with self.voiceover(text="This dual action significantly increases the risk of bleeding complications."):
            self.play(Write(effect_text))
            self.wait(1)

        # Warning box
        warning_box = VGroup(
            Rectangle(height=2, width=6, fill_opacity=0.1, color=RED),
            Text("⚠ Medical Supervision Required", font_size=32, color=RED),
            Text("Monitor for:", font_size=28),
            Text("• Unusual bleeding", font_size=24),
            Text("• Easy bruising", font_size=24),
            Text("• Dark stools", font_size=24)
        ).arrange(DOWN, buff=0.2)
        
        with self.voiceover(text="Due to these serious risks, this combination requires careful medical supervision and monitoring for signs of bleeding."):
            self.play(
                FadeOut(vessel),
                FadeOut(blood_cells),
                FadeOut(effect_text),
                FadeIn(warning_box)
            )
            self.wait(1)

        # Conclusion
        conclusion = VGroup(
            Text("Key Takeaways:", font_size=36, color=YELLOW),
            Text("• Always inform your healthcare provider", font_size=28),
            Text("• Regular monitoring is essential", font_size=28),
            Text("• Report any unusual symptoms immediately", font_size=28)
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2)

        with self.voiceover(text="Remember to always inform your healthcare provider about all medications you're taking and follow their monitoring instructions carefully."):
            self.play(
                FadeOut(warning_box),
                FadeIn(conclusion)
            )
            self.wait(2)

        # Final fade out
        with self.voiceover(text="Your safety depends on proper medical supervision and careful monitoring of these medications."):
            self.play(
                FadeOut(title),
                FadeOut(warfarin_group),
                FadeOut(aspirin_group),
                FadeOut(conclusion),
                run_time=2
            )
            self.wait(1)