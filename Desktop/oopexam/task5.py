class Nobel:
    def __init__(self, category , year , winner ) :
       self.category = category
       self.year = year
       self.winner = winner 

    def nishon(self):
        print(f"nobel in {self.category}, {self.year}:{self.winner}")

nobelprizz = Nobel("Phythik", 1987 , "Mary Kyuri")
nobelprizz.nishon

    