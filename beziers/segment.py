from beziers.point import Point

class Segment(object):
  def __getitem__(self, item):
    return self.points[item]
  def __len__(self):
    return len(self.points)

  @property
  def start(self):
    return self.points[0]

  @property
  def end(self):
    return self.points[-1]

  def translate(self,vector):
    klass = self.__class__
    return klass(*[ p+vector for p in self.points ])

  def rotate(self,around, by):
    klass = self.__class__
    pNew = [ p.clone() for p in self.points]
    for p in pNew: p.rotate(around,by)
    return klass(*pNew)

  def align(self):
    t1 = self.translate(self.start * -1)
    t2 = t1.rotate(Point(0,0),t1.end.angle * -1)
    return t2