class Employee:
  def __init__(self, name, salery ,id):

    self.name = name 
    self._salery = salery
    self._-id = id 
  def nishon_dodan(self) :
    print(self.name)
  def scrt(self):
    print(f"oylik:{self._salery}")
    print(f"raqam_id ->{self.__id}")
bobo = Employee("Bobojun" ,2500,  1 )
bobo.nishon_dodan
bobo.scrt
    