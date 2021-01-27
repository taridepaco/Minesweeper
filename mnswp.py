# import PIL.ImageGrab
import pyautogui as pya
import numpy as np
from time import sleep
import cProfile, pstats, io
from pstats import SortKey

frame=(61,256, 449, 449)
n=16
mnn=40
xt=0
cx_rgbd = np.array([[140,140,205,57],
                    [111,161,111,61],
                    [214,115,115,61],
                    [121,121,165,61],
                    [159,106,106,61],
                    [103,158,158,44],
                    [136,136,136,73],
                    [157,157,157,27],
                    [178,151,151,75],
                    [101,101,101,81],
                    [146,83,83,80],
                    [134,7,7,58],
                    [188,188,188,1],
                    [197,197,197,20]])
cx_lbl = [1,2,3,4,5,6,7,8,-2,-3,-3,-3,0,-1]

class mnswp_game:
    def __init__(self,frame,rw,cl,mnn):
        self.frame = frame
        self.rows = rw
        self.colms = cl
        self.mnes = mnn
        self.cxi = (np.arange(self.colms)/self.colms*self.frame[2]//1).astype('int')+3
        self.cxj = (np.arange(self.rows)/self.rows*self.frame[3]//1).astype('int')+3
        self.cxw = np.mean(np.diff(self.cxi)).astype('int')-6
        self.rstxy = (self.frame[0]+self.frame[2]/2,self.frame[1]-2*self.cxw)
        self.pr = cProfile.Profile()
        self.pr.enable()

    def mnswp_tab(self):
        a = pya.screenshot(region=self.frame)
        self.tab = np.zeros((self.rows,self.colms),dtype=int)-1
        for j in range(self.rows):
            for i in range(self.colms):
                ab=a.crop(box=(self.cxi[i],self.cxj[j],self.cxi[i]+self.cxw,self.cxj[j]+self.cxw))
                ab.R = list(ab.getdata(band=0))
                ab.G = list(ab.getdata(band=1))
                ab.B = list(ab.getdata(band=2))
                ab.Rm, ab.Rd = mnswp_cxmd(ab.R)
                ab.Gm, ab.Gd = mnswp_cxmd(ab.G)
                ab.Bm, ab.Bd = mnswp_cxmd(ab.B)
                ab.d = np.mean([ab.Rd,ab.Gd,ab.Bd]).astype('int')
                self.tab[j,i] = mnsw_cx_fnd(ab) # revisar si ji o ij
        return self


    def mnswp_state(self):
        if np.sum(self.tab == -1) == 0:
            print('WON!')
            # exit()
            self.pr.disable()
            s = io.StringIO()
            sortby = SortKey.CUMULATIVE
            ps = pstats.Stats(self.pr, stream=s).sort_stats(sortby)
            ps.print_stats()
            print(s.getvalue())
            self.running = False
        elif -3 in self.tab:
            self.running = False
        else:
            self.running = True
        return self



    def mnswp_act(self):
        if self.running:
            # print(self.tab)
            f=0
            for j in range(self.rows):
                for i in range(self.colms):
                    if self.tab[j,i] > 0:
                        c = self.tab[max([j-1,0]):min([j+2,self.colms]),max([i-1,0]):min([i+2,self.rows])]
                        # cb = c == -2
                        # c0 = c == -1
                        # poner banderas
                        if (self.tab[j,i] - np.sum(c == -2)) == np.sum(c == -1) and np.sum(c == -1) > 0:
                            # print(self.tab[j,i],np.sum(c == -2),np.sum(c == -1))
                            # pulsar boton derecho los -1 de ese cuadrante
                            # sleep(xt)
                            for jj in range(max([j-1,0]),min([j+2,self.colms])):
                                for ii in range(max([i-1,0]),min([i+2,self.rows])):
                                    if self.tab[jj,ii] == -1:
                                        X,Y=mnswp_ij2xy(self,ii,jj)
                                        pya.click(x=X, y=Y, button='right')
                                        f=1
                            self.mnswp_tab()
                            continue
                        # clicar safe
                        if (self.tab[j,i] - np.sum(c == -2)) == 0 and np.sum(c == -1) > 0:
                            # sleep(xt)
                            # pulsar todos los -1 de ese cuadrante 
                            for jj in range(max([j-1,0]),min([j+2,self.colms])):
                                for ii in range(max([i-1,0]),min([i+2,self.rows])):
                                    if self.tab[jj,ii] == -1:
                                        X,Y=mnswp_ij2xy(self,ii,jj)
                                        pya.click(x=X, y=Y)
                                        f=1
                                        self.mnswp_tab()
                                        continue
                            # continue
                    else:
                        continue
            # clicar random
            if f==0:
                ri=np.random.randint(self.rows)
                while -1 not in self.tab[:,ri]:
                    ri=np.random.randint(self.rows)
                rj=np.random.randint(self.colms)
                while self.tab[rj,ri] != -1:
                    rj=np.random.randint(self.colms)
                # sleep(xt)
                X,Y=mnswp_ij2xy(self,ri,rj)
                pya.click(x=X, y=Y)





            
        else:
            #click the smiley to start a new game and click in a random position
            # sleep(xt)
            pya.click(x=self.rstxy[0], y=self.rstxy[1])
            i=np.random.randint(self.rows)
            j=np.random.randint(self.colms)
            X,Y=mnswp_ij2xy(self,i,j)
            # sleep(xt)
            pya.click(x=X, y=Y)

def mnswp_ij2xy(self,i,j):
    x = self.frame[0]+self.cxi[i]+self.cxw/2
    y = self.frame[1]+self.cxj[j]+self.cxw/2
    return x,y




def mnswp_cxmd(v):
    return np.mean(v).astype('int'),np.std(v).astype('int')

def mnsw_cx_fnd(cx):
    v = np.array([cx.Rm,cx.Gm,cx.Bm,cx.d])
    ds = [np.linalg.norm(v-k) for k in cx_rgbd]
    # print(ds)
    return cx_lbl[ds.index(min(ds))]


def main():
    game = mnswp_game(frame,n,n,mnn)
    while True:
        game.mnswp_tab()
        game.mnswp_state()
        game.mnswp_act()
        # break
        





if __name__ == "__main__":
    main()