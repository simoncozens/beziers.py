import sys
from beziers.utils.intersectionsmixin import Intersection

class BooleanOperationsMixin:
  booleanOperators = {
    'unite': { '1': True, '2': True },
    'intersect': { '2': True },
    'subtract':  { '1': True },
    'exclude':   { '1': True, '-1': True }
  }

  def getSelfIntersections(self):
    segs = self.asSegments()
    intersections = []
    for seg in segs:
      l = seg.hasLoop
      if l and l[0]>0 and l[0]<1 and l[1]>0 and l[0]<1:
        intersections.append(Intersection(seg,l[0], seg,l[1]))
    for i1 in range(0, len(segs)):
      for i2 in range (i1+1, len(segs)):
        for i in segs[i1].intersections(segs[i2]):
          if i.t1 > 1e-2 and i.t1 < 1-1e-2:
            intersections.append(i)
    return intersections

  def removeOverlap(self):
    if not self.closed:
      raise "Can only remove overlap on closed paths"
