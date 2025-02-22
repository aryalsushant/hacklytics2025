import os
from manim import *
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.gtts import GTTSService

class DrugInteraction(VoiceoverScene):
    def construct(self):
        self.set_speech_service(GTTSService())

        # Introduction
        title = Text("Warfarin & Aspirin Interaction", font_size=48).to_edge(UP, buff=0.5)
        
        with self.voiceover(text="Let's understand the interaction between Warfarin and Aspirin, two medications that affect blood clotting."):
            self.play(Write(title))
            self.wait(1)

        # Drug Visualization
        warfarin_svg = SVGMobject("warfarin.svg").scale(0.5).move_to(LEFT * 3)
        aspirin_svg = SVGMobject("aspirin.svg").scale(0.5).move_to(RIGHT * 3)

        warfarin_text = Text("Warfarin", color=RED).next_to(warfarin_svg, UP)
        aspirin_text = Text("Aspirin", color=BLUE).next_to(aspirin_svg, UP)

        with self.voiceover(text="Here are the molecular structures of Warfarin and Aspirin."):
            self.play(Create(warfarin_svg), Write(warfarin_text), Create(aspirin_svg), Write(aspirin_text))
            self.wait(1)

        # Drug Functions
        warfarin_function = Text("Warfarin: Anticoagulant (Blood Thinner)", color=RED, font_size=24).next_to(warfarin_svg, DOWN)
        aspirin_function = Text("Aspirin: Antiplatelet (Prevents Clotting)", color=BLUE, font_size=24).next_to(aspirin_svg, DOWN)

        with self.voiceover(text="Warfarin is an anticoagulant that prevents blood clots, while Aspirin is an antiplatelet drug that reduces clot formation."):
            self.play(Write(warfarin_function), Write(aspirin_function))
            self.wait(1)

        # Interaction Process
        interaction_text = Text("Combined use increases bleeding risk!", color=YELLOW, font_size=36).move_to(DOWN * 2)

        with self.voiceover(text="When taken together, Warfarin and Aspirin can significantly increase the risk of bleeding because they both affect blood clotting through different mechanisms."):
            self.play(Write(interaction_text))
            self.wait(1)

        # Side Effects
        side_effects = VGroup(
            Text("Increased bleeding risk", color=RED, font_size=24),
            Text("Bruising", color=RED, font_size=24),
            Text("Potential internal bleeding", color=RED, font_size=24)
        ).arrange(DOWN)
        side_effects.next_to(interaction_text, DOWN)

        with self.voiceover(text="The major side effects of this interaction include increased bleeding, easy bruising, and the potential for serious internal bleeding."):
            self.play(Write(side_effects))
            self.wait(1)

        # Medical Recommendations
        recommendations = VGroup(
            Text("Medical supervision required", color=YELLOW, font_size=24),
            Text("Regular monitoring is crucial", color=YELLOW, font_size=24),
            Text("Inform your doctor", color=YELLOW, font_size=24)
        ).arrange(DOWN)
        recommendations.to_edge(DOWN)

        with self.voiceover(text="This combination requires close medical supervision and regular monitoring. Always inform your doctor about all medications you are taking."):
            self.play(Write(recommendations))
            self.wait(1)

        # Final Fade Out
        with self.voiceover(text="Your safety depends on careful monitoring and communication with your healthcare provider. Thank you."):
            self.play(
                FadeOut(title),
                FadeOut(warfarin_svg),
                FadeOut(aspirin_svg),
                FadeOut(warfarin_text),
                FadeOut(aspirin_text),
                FadeOut(warfarin_function),
                FadeOut(aspirin_function),
                FadeOut(interaction_text),
                FadeOut(side_effects),
                FadeOut(recommendations),
                run_time=2
            )
            self.wait(1)