from manim import *
class SquareToCircle(Scene):
    def construct(self):
        circle = Circle()  # create a circle
        circle.set_fill(PINK, opacity=0.5)  # set color and transparency

        square = Square()  # create a square
        square.rotate(PI / 4)  # rotate a certain amount

        self.play(Create(square))  # animate the creation of the square
        self.play(Transform(square, circle))  # interpolate the square into the circle
        self.play(FadeOut(square))  # fade out animation


class Pigsort(Scene):
    def construct(self):
        listitems = [500,244,372,109,85,6,400,355]
        intManim =  [Text(f"{x}", font_size=36) for x in listitems]
        intgroup = VGroup(*intManim).set_x(0).arrange_in_grid(rows=len(intManim),cols=1,buff=0.2, flow_order='dr')
        self.play(AnimationGroup(*[FadeIn(i,scale=1.1) for i in intgroup], lag_ratio=0.05, duration=1))

        pigholes = VGroup(*[Text(str(x),font_size=36) for x in range(8)]).arrange_in_grid(rows=1, cols=8, buff=0.75, flow_order='rd').to_edge(UP)
        self.play(intgroup.animate(duration=0.5).to_edge(LEFT),AnimationGroup(*[FadeIn(i) for i in pigholes], lag_ratio=0, duration=0.5))
        origin = intgroup.copy()
        self.wait(0.5)
        for it in range(3):
            dig = [Text(f"{(x>>(it*3)) & 7}", font_size=36) for x in listitems]
            diggroup = VGroup(*dig).set_x(0).arrange_in_grid(rows=len(dig),cols=1,buff=0.2, flow_order='dr')
            diggroup.next_to(intgroup, RIGHT, buff=0.5)
            self.play(AnimationGroup(*[FadeIn(i,shift=RIGHT) for i in diggroup], lag_ratio=0, duration=0.5),)
            self.wait(2)
            
            
            buff = [[] for _ in range(8)]
            for i in range(len(intgroup)):
                buff[(listitems[i]>>(it*3)) & 7].append((intgroup[i].copy(),i))
            items = []
            idxs = []
            for i in range(len(buff)):
                if buff[i]!=[]:
                    idxs.extend([j[1] for j in buff[i]])
                    items.extend(iter(
                    VGroup(*[j[0] for j in buff[i]]).arrange_in_grid(
                                    rows=len(buff[i]),
                                    cols=1,
                                    buff=0.1,
                                    flow_order='dr',).next_to(pigholes[i], DOWN, buff=0.25)))        
            ordereditems = VGroup(*[val for (_, val) in sorted(zip(idxs, items), key=lambda x: x[0])])
            for idx, i  in enumerate(intgroup):
                i.generate_target()
                i.target.become(ordereditems[idx])
            self.play(LaggedStart(*[MoveToTarget(g, path_arc=1,run_time=1.5) for g in intgroup],lag_ratio=0.75,duration=10),AnimationGroup(*[FadeOut(i) for i in diggroup], lag_ratio=1.125)
                    )
            # self.play(x)
            self.wait(2)
            items = VGroup(*items)
            targets = items.copy().set_x(0).arrange_in_grid(rows=len(intManim),cols=1,buff=0.1, flow_order='dr').to_edge(LEFT)
            for idx, i in enumerate(targets):
                i.move_to(origin[idx])
            newidx = [0 for _ in idxs]
            for idx, g in enumerate(idxs):
                intgroup[g].target.become(targets[idx])
                newidx[g] = idx
            intgroup = VGroup(*[val for (_, val) in sorted(zip(newidx, intgroup), key=lambda x: x[0])])
            listitems = [val for (_, val) in sorted(zip(newidx, listitems), key=lambda x: x[0])]
            self.play(LaggedStart(*[MoveToTarget(g, path_arc=-1,run_time=1.5) for g in intgroup],lag_ratio=0.5,duration=10), )
            self.wait(2)
        self.wait(5)
        


        
                