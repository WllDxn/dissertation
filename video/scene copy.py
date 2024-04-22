from manim import *
from math import ceil, log
import numpy
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
        listitems = [52,12,44,8,21,6,62]
        intManim =  [Text(f"{x}", font_size=36) for x in listitems]
        intgroup = VGroup(*intManim).set_x(0).arrange_in_grid(rows=len(intManim),cols=1,buff=0.2, flow_order='dr')
        self.play(AnimationGroup(*[FadeIn(i,scale=1.1) for i in intgroup], lag_ratio=0.05, duration=1))
        pigholes = VGroup(*[Text(str(x),font_size=36) for x in range(8)]).arrange_in_grid(rows=1, cols=8, buff=0.75, flow_order='rd').to_edge(UP)
        vlines = [Line(ORIGIN, DOWN, color=WHITE).move_to(p).shift(RIGHT*0.5) for p in pigholes]
        vlines.append(Line(ORIGIN, DOWN, color=WHITE).move_to(pigholes[0]).shift(LEFT*0.5))
        hlines = [Line(ORIGIN, RIGHT*len(pigholes), color=WHITE).move_to(pigholes).shift(UP*0.485).scale(0.99),
                  Line(ORIGIN, LEFT*len(pigholes), color=WHITE).move_to(pigholes).shift(DOWN*0.485).scale(0.99)
                  ]
        self.play(intgroup.animate(duration=0.5).to_edge(LEFT),
                  AnimationGroup(*[FadeIn(i) for i in pigholes], lag_ratio=0, duration=0.5,),
                  AnimationGroup(*[Create(i) for i in vlines], lag_ratio=0, duration=0.5,),
                  AnimationGroup(*[Create(i) for i in hlines], lag_ratio=0, duration=0.5,),
                  )
        self.wait(2)
       
        origin = intgroup.copy()
        self.wait(0.5)
        for it in range(2):
            toss = []
            for i in range(it+1):
                dig = [Text(f"{(x>>(i*3)) & 7}", font_size=36) for x in listitems]
                diggroup = VGroup(*dig).set_x(0).arrange_in_grid(rows=len(dig),cols=1,buff=0.2, flow_order='dr')
                diggroup.next_to(intgroup, RIGHT, buff=0.35)
                for t in toss:
                    t.generate_target()
                    t.target.shift(RIGHT*0.5)
                    t.target.set_color(GREY)
                self.play(AnimationGroup(*[FadeIn(i,shift=RIGHT) for i in diggroup], lag_ratio=0, duration=0.5),
                          *[MoveToTarget(t) for t in toss],
                          )
                self.wait(0.25)
                if i != it:
                    toss+=dig
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
                                    flow_order='dr',).next_to(pigholes[i], DOWN, buff=0.45)))
            ordereditems = VGroup(*[val for (_, val) in sorted(zip(idxs, items), key=lambda x: x[0])])
            for idx, i  in enumerate(intgroup):
                i.generate_target()
                i.target.become(ordereditems[idx])
            self.play(LaggedStart(*[MoveToTarget(g, path_arc=0.5,run_time=1.5) for g in intgroup],lag_ratio=0.75,duration=10),)
            self.wait()
            if toss != []:
                self.play(AnimationGroup(*[FadeOut(i) for i in diggroup], lag_ratio=0),
                        AnimationGroup(*[FadeOut(t) for t in toss], lag_ratio=0)
                        )
            else:
                self.play(AnimationGroup(*[FadeOut(i) for i in diggroup], lag_ratio=0),)
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
            self.play(LaggedStart(*[MoveToTarget(g, path_arc=-0.5,run_time=1.5) for g in intgroup],lag_ratio=0.5,duration=10), )
            self.wait(2)
        self.wait(5)
        
class Countsort(Scene):
    def construct(self):
        listitems = [61,29,44,7,31,14,8]
        intManim =  [Text(f"{x}", font_size=36) for x in listitems]
        intgroup = VGroup(*intManim).set_x(0).arrange_in_grid(rows=len(intManim),cols=1,buff=0.2, flow_order='dr').shift(DOWN)
        self.play(AnimationGroup(*[FadeIn(i,scale=1.1) for i in intgroup], lag_ratio=0.05, duration=1))
        pigholes = VGroup(*[Text(str(x),font_size=36) for x in range(8)]).arrange_in_grid(rows=1, cols=8, buff=0.75, flow_order='rd').to_edge(UP).shift(RIGHT)
        vlines = [Line(ORIGIN, DOWN, color=WHITE).move_to(p).shift(RIGHT*0.5) for p in pigholes]
        vlines.append(Line(ORIGIN, DOWN, color=WHITE).move_to(pigholes[0]).shift(LEFT*0.5))
        hlines = [Line(ORIGIN, RIGHT*len(pigholes), color=WHITE).move_to(pigholes).shift(UP*0.485).scale(0.99),
                  Line(ORIGIN, LEFT*len(pigholes), color=WHITE).move_to(pigholes).shift(DOWN*0.485).scale(0.99)
                  ]
        self.play(intgroup.animate(duration=0.5).to_edge(LEFT),
                  AnimationGroup(*[FadeIn(i) for i in pigholes], lag_ratio=0, duration=0.5,),
                  AnimationGroup(*[Create(i) for i in vlines], lag_ratio=0, duration=0.5,),
                  AnimationGroup(*[Create(i) for i in hlines], lag_ratio=0, duration=0.5,),
                  )
        self.wait(2)
        timer =1
        for it in range(2):
            toss = []
            print(listitems)
            for i in range(it+1):
                digvals = [(x>>(i*3)) & 7 for x in listitems]
                dig = [Text(f"{x}", font_size=36) for x in digvals]
                diggroup = VGroup(*dig).set_x(0).arrange_in_grid(rows=len(dig),cols=1,buff=0.2, flow_order='dr',aligned_edge=RIGHT)
                diggroup.next_to(intgroup, RIGHT, buff=0.35)
                for t in toss:
                    t.generate_target()
                    t.target.shift(RIGHT*0.5)
                    t.target.set_color(GREY)
                self.play(AnimationGroup(*[FadeIn(i,shift=RIGHT) for i in diggroup], lag_ratio=0, duration=0.5),
                          *[MoveToTarget(t) for t in toss],
                          )
                self.wait(timer*timer*0.25)
                if i != it:
                    toss+=dig
                # if toss != []:
                #     self.play(*[FadeToColor(t, color=GREY) for t in toss])
            # self.wait(timer*timer*2)
            pigcounts = [0 for _ in pigholes]
            pigcountstext = [Text(str(x), font_size=36).next_to(p, DOWN,buff=0.45) for p, x in zip(pigholes, pigcounts)]
            # pigcounts = [pigcounts[d]+1 for d in digvals]
            self.play(AnimationGroup(*[FadeIn(i,shift=DOWN, run_time=timer*0.5) for i in pigcountstext], lag_ratio=0.1, duration=0.5),)
            balltext = VGroup(*[Text(f"{dv}", font_size=28).next_to(d).set_x(diggroup.get_x()).shift(RIGHT*(0.5*(1+it))) for d, dv in zip(diggroup,digvals)])
            balls = VGroup(*[VGroup(bt, Circle(color=DARK_BLUE,fill_opacity=1, z_index=-1).surround(bt)) for bt in balltext])
            # balls = VGroup(*[Circle(0.15,RED,fill_opacity=1).next_to(d).set_x(diggroup.get_x()).shift(RIGHT*(0.5*(1+it))) for d in diggroup])
            self.play(AnimationGroup(*[DrawBorderThenFill(b,run_time=timer*0.5) for b in balls], lag_ratio=0, duration=0.5,),)
            self.wait(timer*timer*2)
            # break
            targets = [[] for _ in pigcounts]

            targets = [b.move_to((float(pigcountstext[d].get_x()), float(pigcountstext[d].get_y()),0)) for b, d in zip(balls.copy(), digvals)]
            shiftmod = [0 for _ in targets]
            for idx, (t, d) in enumerate(list(zip(targets, digvals))):
                pigcounts[d]+=1
                shiftmod[idx] = pigcounts[d]
                t.shift(DOWN*0.5*pigcounts[d])

            self.play(
                AnimationGroup(*[Transform(b,t,path_arc=1,run_time=timer*1) for b,t in zip(balls, targets)], lag_ratio=0.5),                
                      )

            bidxs = numpy.argsort(list(reversed(digvals)))          
            targets = [list(reversed(targets))[j] for j in bidxs]
            shiftmod = [list(reversed(shiftmod))[j] for j in bidxs]
            for b in balls:
                self.remove(b)
            balls = VGroup(*[t for t in targets])
            for t in targets:
                self.remove(t)
            bouncedown = [b.shift(DOWN*(0.25+(0.05*s))) for b,s in zip(balls.copy(), shiftmod)]
            for b,s in zip(balls, shiftmod):
                b.generate_target()
                b.target.shift(UP*0.25*(1+s))
                b.target.scale(0)
            textTargets = [Text(str(x), font_size=36).move_to(p) for p, x in zip(pigcountstext, pigcounts)]
            bounce =AnimationGroup(*[Succession(d, u) for d, u in zip([Transform(b,down,runtime=0.01) for b, down in zip(balls, bouncedown)], [MoveToTarget(mobject=b, runtime=0.01) for b in balls])], lag_ratio=0.05, run_time=timer*1.5)
            self.play(
                AnimationGroup(bounce,AnimationGroup(*[Transform(p,t) for p,t in zip(pigcountstext, textTargets)],lag_ratio=0.05,run_time=timer*0.75), lag_ratio=0.5,),
                
                )
            for idx in range(1,len(pigcounts)):
                pigcounts[idx] += pigcounts[idx-1]
            textTargets = [Text(str(x), font_size=36).move_to(p) for p, x in zip(pigcountstext, pigcounts)]

            self.wait(timer*timer*1)
            self.play(
                AnimationGroup(*[Transform(p,t,run_time=timer*1) for p,t in zip(pigcountstext, textTargets)], lag_ratio=0.5,run_time=timer*1),
                )
            
            self.wait(timer*timer*1)
            newlist = VGroup(*[Text(f"{x}", font_size=36) for x in range(len(intManim))]).arrange_in_grid(rows=len(intManim),cols=1,buff=0.2, flow_order='dr').next_to(intgroup,RIGHT*15)
            hlines = [Line(ORIGIN, LEFT*1.5, color=WHITE).next_to(n,UP,buff=0.1).shift(LEFT*0.5) for n in newlist]
            hlines.append(Line(ORIGIN, LEFT*1.5, color=WHITE).next_to(newlist[-1],DOWN,buff=0.1).shift(LEFT*0.5))
            self.play(intgroup.animate(duration=0.5).to_edge(LEFT),
                  AnimationGroup(*[FadeIn(i) for i in newlist], lag_ratio=0, duration=0.5,),
                  AnimationGroup(*[Create(i) for i in hlines], lag_ratio=0, duration=0.5,),
                  )
            self.wait(timer*timer*1)
            idxs = []
            if toss == []:
                toss=listitems
                run = False
            else:
                run=True
            for val,  dv, dg, ts in reversed(list(zip(intgroup, digvals, diggroup, toss))):
                pigcounts[dv] -=1
                textTargets = [Text(str(x), font_size=36).move_to(p) for p, x in zip(pigcountstext, pigcounts)]
                self.play(
                    AnimationGroup(
                        Circumscribe(VGroup(val,dg),buff=0.15,run_time=0.65),
                        Circumscribe(VGroup(pigholes[dv],pigcountstext[dv]),buff=0.25,run_time=0.75),
                        Transform(pigcountstext[dv],textTargets[dv],run_time=timer*1),lag_ratio=0.5
                    )
                    )
                idxs.append(pigcounts[dv])
                target = val.copy().move_to(newlist[pigcounts[dv]]).shift(LEFT)
                if not run:
                    self.play(
                        AnimationGroup(Transform(val, target,run_time=timer*0.75,path_arc=0.5)),
                        AnimationGroup(FadeOut(dg,run_time=timer*0.5)),
                    )
                else:
                    self.play(
                        AnimationGroup(Transform(val, target,run_time=timer*0.75,path_arc=0.5)),
                        AnimationGroup(FadeOut(dg,run_time=timer*0.5)),
                        AnimationGroup(FadeOut(ts,run_time=timer*0.5)),
                    )
            self.play(intgroup.animate(duration=0.5).to_edge(LEFT),
                    AnimationGroup(*[FadeOut(i,run_time=timer*1) for i in newlist], lag_ratio=0, duration=0.5,),
                    AnimationGroup(*[FadeOut(i,run_time=timer*1) for i in hlines], lag_ratio=0, duration=0.5,),
                    AnimationGroup(*[FadeOut(i,shift=UP,run_time=timer*0.5) for i in pigcountstext], lag_ratio=0.1, duration=0.5),
                    )
            intgroup = VGroup(*[val for (_, val) in sorted(zip(idxs, reversed(intgroup)), key=lambda x: x[0])])
            listitems = [val for (_, val) in sorted(zip(idxs, reversed(listitems)), key=lambda x: x[0])]
            self.wait(timer*timer*1)
            timer = 0.5
        self.wait(2)
            
class Bits(Scene):
    def construct(self):
        input = 326053
        self.play(FadeIn(Text(str(input),font_size=40).to_edge(UP),shift=DOWN))
        base = 8
        basebits = int(ceil(log(input, int(pow(2,base)))))
        bina = [(input>>i)&1 for i in range((basebits*base)-1,-1,-1)]
        binatx = VGroup(*[Text(str(x), font_size=28) for x in bina]).arrange_in_grid(rows=1,cols=len(bina))
        self.play(Create(binatx))
        sl = [
            Line(binatx[-base].get_center(),binatx[-base].get_bottom()).move_to(binatx[-base].get_center()).shift(DOWN*0.25).shift(LEFT*0.21).rotate(PI),
            Line(binatx[-base].get_center(),binatx[-base].get_bottom()).move_to(binatx[-1].get_center()).shift(DOWN*0.25).shift(RIGHT*0.21).rotate(PI),
        ]
        l = Line(sl[0].get_corner(DL), sl[1].get_corner(DR)).shift(UP*0.01)
        lc = [
            Line(l.get_center(),l.get_right()),
            Line(l.get_center(),l.get_left())
        ]
        sl[0].shift(RIGHT*0.02)
        sl[1].shift(LEFT*0.02)
        self.play(Create(lc[0]),Create(lc[1]))
        self.play(AnimationGroup(*[Create(s, run_time=0.5) for s in sl]))
        vals = list(reversed([int(pow(2,j)) for j in range(base)]))
        underline = VGroup(*sl,*lc)
        valstx = VGroup(*[Text(str(x), font_size=28) for x in vals]).arrange_in_grid(rows=1,cols=len(vals)).next_to(underline,DOWN,buff=0.25)
        self.play(Create(valstx))
        underline = VGroup(*sl,*lc, *valstx)
        for i in range(basebits):
            if i==0:
                curr = binatx[-base:]
                currb = bina[-base:]
            elif i==basebits-1:
                curr= binatx[:-base*i]
                currb= bina[:-base*i]
            else:
                curr = binatx[-base*(i+1):-base*i]
                currb = bina[-base*(i+1):-base*i]
            targetvals = [b*p for b, p in zip(currb,vals[-len(curr):])]
            target = [Text(str(x),font_size=28).next_to(o,DOWN) for x, o in zip(targetvals,valstx)]
            self.play(AnimationGroup(*[Transform(c,t) for c,t in zip(curr,target)]))
            targetsum = Text(str(sum(targetvals)),font_size=28).move_to(target[-1])
            self.play(AnimationGroup(*[Transform(c,targetsum) for c in curr]))
            if i != basebits-1:
                self.play(underline.animate(run_time=1).move_to(VGroup(*binatx[-base*(i+2):-base*(i+1)]).get_center()).shift(DOWN*0.5))
        self.wait(4)
        

class Negatives(Scene):
        
    def construct(self):
        inputs = [9,-2,-12,4,-4,15,-4]
        bina = [[] for _ in inputs]
        binatx = [[] for _ in inputs]
        radix = 1
        base = int(pow(2,radix))
        listmax=max(max(inputs), abs(min(inputs)))
        basebits = int(ceil(log(abs(listmax), int(pow(2,radix)))))
        for idx, input in enumerate(inputs):
            # print
            bina[idx] =  [(input>>radix*i)&(base-1) for i in range((basebits),-1,-1)]
            binatx[idx] = VGroup(*[Text(str(x), font_size=28) for x in bina[idx]]).arrange_in_grid(rows=1,cols=len(bina[idx]))
        fullbina = VGroup(*[Text(str(x), font_size=28,stroke_width=1) for y in bina for x in y]).arrange_in_grid(rows=len(bina),cols=len(bina[0]))
        inputtxt = VGroup(*[Text(str(x), font_size=28) for x in inputs]).arrange_in_grid(rows=len(inputs),cols=1,col_alignments='r').to_edge(LEFT).shift(LEFT*1.25)
        vline = Line(inputtxt.copy().scale(1.1).get_corner(UL),inputtxt.copy().scale(1.1).get_corner(DL)).to_edge(RIGHT,buff=0.01)
        self.play(AnimationGroup(Create(vline), inputtxt.animate().to_edge(LEFT,buff=0.26), lag_ratio=0.5))
        fullbina.next_to(vline,RIGHT,buff=0.2)
        self.add(fullbina)
        self.play(fullbina.animate(run_time=1.25).next_to(vline,LEFT,buff=0.35))
        self.wait(0.25)
        indicator = Triangle(color=WHITE,fill_opacity=1).scale(0.125).next_to(fullbina[-1], DOWN, buff=0.25)
        self.play(FadeIn(indicator))
        import numpy
        print(basebits)
        for i in range(1, basebits+2):
            self.play(indicator.animate(run_time=0.5).next_to(fullbina[-i], DOWN, buff=0.25))
            if i==1+(basebits):
                toanim=[]
                for j in range(len(inputs)):
                    bina[j][0] = 0 if bina[j][0] == 1 else 1
                    tmp = Text(str(bina[j][0]),font_size=28).move_to(fullbina[(basebits+1)*j])
                    toanim.append(Transform(fullbina[(basebits+1)*j], tmp))
                self.wait(0.5)
                self.play(AnimationGroup(*toanim))
                self.wait(0.5)
            bit = [x[-i] for x in bina]
            idxs = list(reversed(numpy.argsort(bit)))
            a = 0
            for b in range(base-1, -1, -1):
                z = bit.count(b)
                idxs[a:a+z] = list(reversed(idxs[a:a+z]))
                a+=z
            newfullbina=fullbina.copy()
            newinputtxt=inputtxt.copy()
            tbits=(basebits)+1
            for jdx, j in enumerate(idxs):
                newfullbina[j*(tbits):(j*(tbits))+(tbits)].set_y(fullbina[jdx*(tbits):(jdx*(tbits))+(tbits)].get_y())
                newinputtxt[j].set_y(inputtxt[jdx].get_y())
            
            self.play(Transform(fullbina, newfullbina), Transform(inputtxt, newinputtxt))
            self.wait(0.5)
            inputs = [inputs[j] for j in idxs]
            bina = [bina[j] for j in idxs]
            fullbina = VGroup(*[x for j in idxs for x in fullbina[j*(tbits):(j*(tbits))+(tbits)]])
            inputtxt = VGroup(*[inputtxt[j] for j in idxs])

        self.wait(4)