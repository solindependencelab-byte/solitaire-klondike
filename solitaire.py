import tkinter as tk
from tkinter import messagebox
import random
import copy
import os
import sys

SUITS = ['♠','♥','♦','♣']
RED = {'♥','♦'}
class Solitaire:
    def __init__(self, root):
        self.root=root
        root.title('Solitaire - Klondike')
        self.canvas=tk.Canvas(root,width=1050,height=740,bg='#08703c',highlightthickness=0)
        self.canvas.pack()
        self.canvas.bind('<Button-1>',self.click)
        self.canvas.bind('<Double-Button-1>',self.double)
        self.canvas.bind('<B1-Motion>',self.drag_motion)
        self.canvas.bind('<ButtonRelease-1>',self.drag_release)
        self.drag_start=None
        self.drag_active=False
        tk.Button(root,text='New Game',command=self.new,bg='#e6c77a',fg='#173b2c',font=('Segoe UI',10,'bold'),relief='flat',padx=10,pady=4).place(x=930,y=10)
        tk.Button(root,text='Hint',command=self.hint,bg='#e6c77a',fg='#173b2c',font=('Segoe UI',10,'bold'),relief='flat',padx=10,pady=4).place(x=675,y=10)
        tk.Button(root,text='Undo',command=self.undo,bg='#e6c77a',fg='#173b2c',font=('Segoe UI',10,'bold'),relief='flat',padx=10,pady=4).place(x=855,y=10)
        self.difficulty=tk.StringVar(value='Classic')
        difficulty_menu=tk.OptionMenu(root,self.difficulty,'Easy','Classic','Hard',command=lambda _:self.new())
        difficulty_menu.configure(bg='#e6c77a',fg='#173b2c',font=('Segoe UI',10,'bold'),relief='flat',bd=0,highlightthickness=0,activebackground='#f2d997',activeforeground='#173b2c',padx=8,pady=4,cursor='hand2')
        difficulty_menu['menu'].configure(bg='#f5e8c5',fg='#173b2c',font=('Segoe UI',10),activebackground='#e6c77a',activeforeground='#173b2c')
        difficulty_menu.place(x=745,y=10)
        root.bind('<Control-z>',lambda event:self.undo())
        self.card_images={}
        assets=os.path.join(getattr(sys,'_MEIPASS',os.path.dirname(os.path.abspath(__file__))),'card_images')
        for suit in ('spade','heart','diamond','club'):
            for n in range(1,14):
                self.card_images[(n,suit)]=tk.PhotoImage(file=os.path.join(assets,f'{suit}_{n}.png'))
        self.card_images['back']=tk.PhotoImage(file=os.path.join(assets,'back.png'))
        self.new()
    def new(self):
        deck=[(n,s) for s in SUITS for n in range(1,14)]
        random.shuffle(deck)
        self.stock=deck[28:];self.waste=[];self.found=[[] for _ in range(4)]
        self.score=0;self.moves=0;self.passes=0
        self.cols=[];self.up=[]
        i=0
        for j in range(7):
            self.cols.append(deck[i:i+j+1]);self.up.append(([False]*max(0,j-1)+[True]*min(j+1,2)) if self.difficulty.get()=='Easy' else ([False]*j+[True]));i+=j+1
        self.sel=None;self.history=[];self.drag_start=None;self.drag_active=False;self.hint_marks=None;self.hint_text='';self.draw()
    def save(self):
        self.history.append(copy.deepcopy((self.stock,self.waste,self.found,self.cols,self.up,self.score,self.moves,self.passes)))
    def undo(self):
        if not self.history:return
        self.stock,self.waste,self.found,self.cols,self.up,self.score,self.moves,self.passes=self.history.pop()
        self.sel=None;self.hint_marks=None;self.hint_text='';self.draw()
    def card(self,x,y,c,face=True,selected=False):
        cv=self.canvas
        cv.create_rectangle(x+3,y+4,x+94,y+129,fill='#125c39',outline='')
        key=(c[0],{'♠':'spade','♥':'heart','♦':'diamond','♣':'club'}[c[1]]) if face else 'back'
        cv.create_rectangle(x,y,x+92,y+125,fill='#fffefa',outline='#f4c65a' if selected else '#deded5',width=3 if selected else 1)
        cv.create_image(x+2,y,anchor='nw',image=self.card_images[key])
        if selected:cv.create_rectangle(x,y,x+92,y+125,outline='#ffd54b',width=3)
        return
        cv.create_rectangle(x+4,y+5,x+96,y+130,fill='#06432f',outline='')
        cv.create_rectangle(x,y,x+92,y+125,fill='#fffdf6' if face else '#b92f45',outline='#f4c65a' if selected else '#d6d4c8',width=3 if selected else 1)
        cv.create_line(x+2,y+2,x+90,y+2,fill='#ffffff' if face else '#f5cbd2')
        if face:
            n,s=c;v={1:'A',11:'J',12:'Q',13:'K'}.get(n,str(n))
            color='#c72e42' if s in RED else '#202a35'
            cv.create_text(x+8,y+6,text=v,anchor='nw',font=('Segoe UI',18,'bold'),fill=color)
            cv.create_text(x+11,y+31,text=s,anchor='nw',font=('Segoe UI Symbol',16),fill=color)
            cv.create_text(x+82,y+118,text=v,anchor='se',font=('Segoe UI',14,'bold'),fill=color)
            if n in (11,12,13):
                cv.create_rectangle(x+25,y+34,x+69,y+109,fill='#f8ecd5',outline='#a99a80')
                cv.create_polygon(x+29,y+59,x+47,y+39,x+65,y+59,fill='#c7a75c',outline='#816a3a')
                cv.create_oval(x+36,y+52,x+58,y+77,fill='#e8c5a5',outline='#8a5a4a')
                cv.create_arc(x+31,y+72,x+63,y+111,start=0,extent=180,fill='#305b8b' if n==13 else '#b83d54',outline='#293a50',style='pieslice')
                cv.create_text(x+47,y+96,text=v,font=('Georgia',18,'bold'),fill='#fff5d8')
            elif n==1:
                cv.create_text(x+46,y+70,text=s,font=('Segoe UI Symbol',49),fill=color)
            else:
                positions={2:[(46,44),(46,95)],3:[(46,40),(46,70),(46,100)],4:[(29,44),(63,44),(29,96),(63,96)],5:[(29,44),(63,44),(46,70),(29,96),(63,96)],6:[(29,39),(63,39),(29,70),(63,70),(29,101),(63,101)],7:[(29,39),(63,39),(46,54),(29,70),(63,70),(29,101),(63,101)],8:[(29,39),(63,39),(46,53),(29,70),(63,70),(46,87),(29,101),(63,101)],9:[(29,36),(63,36),(29,57),(63,57),(46,70),(29,83),(63,83),(29,104),(63,104)],10:[(29,36),(63,36),(46,47),(29,57),(63,57),(29,83),(63,83),(46,94),(29,104),(63,104)]}
                for px,py in positions.get(n,[]):cv.create_text(x+px,y+py,text=s,font=('Segoe UI Symbol',17,'bold'),fill=color)
        else:
            cv.create_rectangle(x+6,y+6,x+86,y+119,outline='#fff1ed',width=2)
            cv.create_rectangle(x+11,y+11,x+81,y+114,outline='#f7d0d4',width=1)
            for yy in range(19,112,10):
                for xx in range(19,80,10):
                    cv.create_oval(x+xx-2,y+yy-2,x+xx+2,y+yy+2,fill='#f6bec8',outline='')
            cv.create_polygon(x+46,y+42,x+69,y+62,x+46,y+84,x+23,y+62,fill='#fff9ed',outline='#e5d2c7',width=2)
            cv.create_text(x+46,y+62,text='S',font=('Georgia',22,'bold'),fill='#b92f45')
    def draw(self):
        c=self.canvas;c.delete('all')
        c.create_rectangle(0,0,1050,740,fill='#188044',outline='')
        for y in range(0,740,6):
            c.create_line(0,y,1050,y,fill='#188044' if y%12==0 else '#197e45')
        # Subtle Batman-style bat emblem on the felt, behind the playing cards.
        cx,cy=525,480
        shape=[(-240,-25),(-190,-70),(-135,-62),(-92,-28),(-65,-60),(-36,-52),(-15,-93),(-7,-83),(0,-111),(7,-83),(15,-93),(36,-52),(65,-60),(92,-28),(135,-62),(190,-70),(240,-25),(185,-8),(151,38),(113,12),(78,62),(45,25),(0,95),(-45,25),(-78,62),(-113,12),(-151,38),(-185,-8)]
        coords=[v for x,y in shape for v in (cx+x,cy+y)]
        c.create_oval(cx-260,cy-125,cx+260,cy+125,fill='#257c42',outline='#3c9253',width=3)
        c.create_polygon(*coords,fill='#155b35',outline='#286f40',width=2)
        c.create_rectangle(0,0,1050,48,fill='#103e31',outline='')
        c.create_line(0,48,1050,48,fill='#b99b5c',width=2)
        c.create_text(20,11,text='SOLITAIRE',anchor='nw',font=('Georgia',21,'bold'),fill='#f4e4bb')
        c.create_text(255,22,text='KLONDIKE  |  '+self.difficulty.get().upper(),anchor='nw',font=('Segoe UI',10),fill='#a9c9b7')
        c.create_text(485,21,text=f'SCORE  {self.score}     MOVES  {self.moves}',anchor='nw',font=('Segoe UI',11,'bold'),fill='#f4e4bb')
        for x,label in [(20,'STOCK'),(130,'WASTE'),(460,'FOUNDATIONS')]:
            c.create_text(x,58,text=label,anchor='nw',font=('Segoe UI',9,'bold'),fill='#e8d6a3')
        for x in [20,130,460,570,680,790]:
            c.create_rectangle(x,80,x+92,205,outline='#63917a',width=2,dash=(5,4))
        if self.stock:self.card(20,80,None,False)
        else:c.create_text(66,140,text='↻',font=('Arial',36),fill='white')
        if self.waste:self.card(130,80,self.waste[-1],selected=self.sel==('w',0))
        for j,pile in enumerate(self.found):
            if pile:self.card(460+110*j,80,pile[-1],selected=self.sel==('f',j))
        for j,col in enumerate(self.cols):
            x=20+j*145
            c.create_rectangle(x,265,x+92,390,outline='#63917a',width=2,dash=(5,4))
            for k,card in enumerate(col):
                self.card(x,265+28*k,card,self.up[j][k],self.sel==('c',j,k))
        if self.hint_marks:
            for x,y in self.hint_marks:
                c.create_rectangle(x-3,y-3,x+95,y+128,outline='#ffe36c',width=4)
        if self.hint_text:
            c.create_rectangle(235,215,1000,249,fill='#103e31',outline='#d6b66b',width=1)
            c.create_text(249,232,text=self.hint_text,anchor='w',font=('Segoe UI',11,'bold'),fill='#fff1b9')
        c.create_rectangle(0,698,1050,740,fill='#103e31',outline='')
        c.create_line(0,698,1050,698,fill='#b99b5c')
        c.create_text(20,712,text='DRAG cards or stacks   •   DOUBLE-CLICK to auto-move   •   CTRL+Z to undo',anchor='nw',fill='#e6dfc9',font=('Segoe UI',10))
        c.create_text(1030,712,text='Hard: draw 3, 3 passes' if self.difficulty.get()=='Hard' else 'Draw 1, unlimited passes',anchor='ne',fill='#e6dfc9',font=('Segoe UI',9))
        if all(len(p)==13 for p in self.found):messagebox.showinfo('Solitaire','You win!')
    def hint(self):
        # Advisory only: no cards, score, or move counter are changed.
        options=[]
        def add(card,source,origin,priority):
            for j in range(4):
                if self.can_found(card,j):
                    options.append((priority,source,origin,(460+110*j,80),
                                    'Move '+self.card_name(card)+' to a foundation.'))
            for j in range(7):
                if source[0]=='c' and source[1]==j:continue
                if self.can_col(card,j):
                    # Avoid shuffling a King from one empty column to another.
                    if source[0]=='c' and source[2]==0 and len(self.cols[source[1]])==1 and not self.cols[j]:continue
                    options.append((priority+2,source,origin,(20+145*j,265+28*len(self.cols[j])),
                                    'Move '+self.card_name(card)+' to column '+str(j+1)+'.'))
        for j,col in enumerate(self.cols):
            if not col:continue
            for k in range(len(col)):
                if not self.up[j][k]:continue
                # A valid descending alternating-color face-up run is required.
                run=col[k:]
                if any(run[i][0]!=run[i+1][0]+1 or ((run[i][1] in RED)==(run[i+1][1] in RED)) for i in range(len(run)-1)):continue
                priority=0 if k>0 and not self.up[j][k-1] else 5
                if k==len(col)-1:
                    for f in range(4):
                        if self.can_found(col[k],f):
                            options.append((priority-2,('c',j,k),(20+145*j,265+28*k),(460+110*f,80),
                                            'Move '+self.card_name(col[k])+' to a foundation.'))
                for target in range(7):
                    if target==j or not self.can_col(col[k],target):continue
                    if k==0 and len(col)==1 and not self.cols[target]:continue
                    options.append((priority+2,('c',j,k),(20+145*j,265+28*k),
                                    (20+145*target,265+28*len(self.cols[target])),
                                    'Move '+self.card_name(col[k])+' to column '+str(target+1)+'.'))
        if self.waste:add(self.waste[-1],('w',0),(130,80),3)
        if options:
            options.sort(key=lambda x:x[0])
            _,source,origin,dest,msg=options[0]
            self.hint_marks=[origin,dest]
            self.hint_text='HINT: '+msg
        elif self.stock:
            self.hint_marks=[(20,80)]
            self.hint_text='HINT: Draw from the stock pile.'
        elif self.waste and (self.difficulty.get()!='Hard' or self.passes<2):
            self.hint_marks=[(20,80)]
            self.hint_text='HINT: Recycle the waste pile to the stock.'
        else:
            self.hint_marks=None
            self.hint_text='No legal moves found. Try Undo or start a new game.'
        self.draw()
    def card_name(self,card):
        return {1:'Ace',11:'Jack',12:'Queen',13:'King'}.get(card[0],str(card[0]))+' of '+{'♠':'Spades','♥':'Hearts','♦':'Diamonds','♣':'Clubs'}[card[1]]
    def can_found(self,c,j):
        p=self.found[j]
        return (not p and c[0]==1) or (bool(p) and p[-1][1]==c[1] and c[0]==p[-1][0]+1)
    def can_col(self,c,j):
        p=self.cols[j]
        return (not p and c[0]==13) or (bool(p) and self.up[j][-1] and p[-1][0]==c[0]+1 and (p[-1][1] in RED)!=(c[1] in RED))
    def move(self,dest,j):
        if not self.sel:return
        s=self.sel;cards=[]
        if s[0]=='w' and self.waste:cards=[self.waste[-1]]
        elif s[0]=='f' and self.found[s[1]]:cards=[self.found[s[1]][-1]]
        elif s[0]=='c':cards=self.cols[s[1]][s[2]:]
        if not cards:return
        if dest=='f':
            if len(cards)!=1 or not self.can_found(cards[0],j):return
        elif dest=='c':
            if s[0]=='c' and s[1]==j:return
            if not self.can_col(cards[0],j):return
        self.save()
        self.hint_marks=None;self.hint_text=''
        self.moves+=1
        if dest=='f':self.score+=10
        elif s[0]=='w' and dest=='c':self.score+=5
        if s[0]=='w':self.waste.pop()
        elif s[0]=='f':self.found[s[1]].pop()
        else:
            self.cols[s[1]]=self.cols[s[1]][:s[2]]
            self.up[s[1]]=self.up[s[1]][:s[2]]
            if self.up[s[1]] and not self.up[s[1]][-1]:
                self.up[s[1]][-1]=True;self.score+=5
        if dest=='f':self.found[j].extend(cards)
        else:self.cols[j].extend(cards);self.up[j].extend([True]*len(cards))
        self.sel=None;self.draw()
    def click(self,e):
        self.drag_start=(e.x,e.y)
        self.drag_active=False
        x,y=e.x,e.y
        if 80<=y<=205:
            if 20<=x<=112:
                if self.stock:
                    self.save()
                    self.hint_marks=None;self.hint_text=''
                    count=3 if self.difficulty.get()=='Hard' else 1
                    for _ in range(min(count,len(self.stock))):self.waste.append(self.stock.pop())
                    self.moves+=1
                elif self.waste and (self.difficulty.get()!='Hard' or self.passes<2):
                    self.save();self.hint_marks=None;self.hint_text='';self.stock=self.waste[::-1];self.waste=[];self.passes+=1;self.moves+=1
                self.sel=None;self.draw();return
            if 130<=x<=222 and self.waste:
                self.sel=('w',0);self.draw();return
            for j in range(4):
                if 460+j*110<=x<=552+j*110:
                    if self.sel:self.move('f',j)
                    elif self.found[j]:self.sel=('f',j);self.draw()
                    return
        if y>=265:
            for j in range(7):
                left=20+j*145
                if left<=x<=left+92:
                    col=self.cols[j]
                    if self.sel:
                        old=self.sel
                        self.move('c',j)
                        if self.sel is None:return
                        self.sel=None
                    for k in range(len(col)-1,-1,-1):
                        if self.up[j][k] and 265+28*k<=y<=265+28*k+125:
                            self.sel=('c',j,k);break
                    self.draw();return
        self.sel=None;self.draw()
    def drag_motion(self,e):
        if not self.drag_start or not self.sel:return
        sx,sy=self.drag_start
        if abs(e.x-sx)+abs(e.y-sy)<10:return
        self.drag_active=True
        self.canvas.delete('drag_preview')
        s=self.sel
        if s[0]=='c':cards=self.cols[s[1]][s[2]:]
        elif s[0]=='w' and self.waste:cards=[self.waste[-1]]
        elif s[0]=='f' and self.found[s[1]]:cards=[self.found[s[1]][-1]]
        else:return
        for k,card in enumerate(cards):
            x=e.x-46;y=e.y-45+28*k
            self.canvas.create_rectangle(x,y,x+92,y+125,fill='#fff9e8',outline='#ffd44d',width=2,tags='drag_preview')
            n,suit=card;v={1:'A',11:'J',12:'Q',13:'K'}.get(n,str(n))
            color='#c52535' if suit in RED else '#111111'
            self.canvas.create_text(x+8,y+8,text=v+suit,anchor='nw',font=('Arial',16,'bold'),fill=color,tags='drag_preview')
    def drag_release(self,e):
        self.drag_start=None
        if not self.drag_active:return
        self.drag_active=False
        self.canvas.delete('drag_preview')
        x,y=e.x,e.y
        if 80<=y<=205:
            for j in range(4):
                if 460+110*j<=x<=552+110*j:
                    self.move('f',j);self.draw();return
        if y>=265:
            for j in range(7):
                if 20+145*j<=x<=112+145*j:
                    self.move('c',j);self.draw();return
        self.draw()
    def double(self,e):
        x,y=e.x,e.y
        if 130<=x<=222 and 80<=y<=205 and self.waste:self.sel=('w',0)
        elif y>=265:
            for j,col in enumerate(self.cols):
                if 20+j*145<=x<=112+j*145 and col:
                    for k in range(len(col)-1,-1,-1):
                        if self.up[j][k] and 265+28*k<=y<=265+28*k+125:
                            self.sel=('c',j,k);break
                    break
        if self.sel:
            for j in range(4):
                old=self.sel;self.move('f',j)
                if self.sel is None:return
        if self.sel:
            s=self.sel
            if s[0]=='w' and self.waste:card=self.waste[-1]
            elif s[0]=='c' and self.cols[s[1]]:card=self.cols[s[1]][-1]
            else:card=None
            if card:
                if s[0]=='c':card=self.cols[s[1]][s[2]]
                for j in range(7):
                    if s[0]=='c' and s[1]==j:continue
                    if self.can_col(card,j):
                        self.move('c',j);return
        self.draw()

if __name__=='__main__':
    root=tk.Tk();Solitaire(root);root.mainloop()

[executed on device: TARDIS (854d724b-8211-4481-9d4b-2dc82524eee6)]