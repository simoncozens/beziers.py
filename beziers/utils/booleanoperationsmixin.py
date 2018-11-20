import sys
from beziers.path.representations.Segment import SegmentRepresentation
from beziers.utils.intersectionsmixin import Intersection

class BooleanOperationsMixin:
  booleanOperators = {
    'unite': { '1': True, '2': True },
    'intersect': { '2': True },
    'subtract':  { '1': True },
    'exclude':   { '1': True, '-1': True }
  }

  def getSelfIntersections(self):
    """Returns a list of a path's self-intersections as Intersection objects."""

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
    """Resolves a path's self-intersections by 'walking around the outside'."""
    if not self.closed:
      raise "Can only remove overlap on closed paths"
    splitlist = []
    splitpoints = {}
    def roundoff(point):
      return (int(point.x*1),int(point.y*1))

    for i in self.getSelfIntersections():
      splitlist.append((i.seg1,i.t1))
      splitlist.append((i.seg2,i.t2))
      splitpoints[roundoff(i.point)] = {"in":[], "out": []}
    self.splitAtPoints(splitlist)
    # Trace path
    segs = self.asSegments()
    for i in range(0,len(segs)):
      seg = segs[i]
      if i < len(segs)-1:
        seg.next = segs[i+1]
      else:
        seg.next = segs[0]
      seg.visited = False
      segWinding = self.windingNumberOfPoint(seg.pointAtTime(0.5))
      seg.windingNumber = segWinding
      if roundoff(seg.end) in splitpoints:
        splitpoints[roundoff(seg.end)]["in"].append(seg)
      if roundoff(seg.start) in splitpoints:
        splitpoints[roundoff(seg.start)]["out"].append(seg)
    newsegs = []
    copying = True
    # print("Split points:", splitpoints)
    seg = segs[0]
    while not seg.visited:
      # print("Starting at %s, visiting %s" % (seg.start, seg))
      newsegs.append(seg)
      seg.visited = True
      if roundoff(seg.end) in splitpoints and len(splitpoints[roundoff(seg.end)]["out"]) > 0:
        # print("\nI am at %s and have a decision: " % seg.end)
        inAngle = seg.tangentAtTime(1).angle
        # print("My angle is %s" % inAngle)
        # print("Options are: ")
        # for s in splitpoints[roundoff(seg.end)]["out"]:
          # print(s.end, s.tangentAtTime(0).angle, self.windingNumberOfPoint(s.pointAtTime(0.5)))
        # Filter out the inside points
        splitpoints[roundoff(seg.end)]["out"] = [ o for o in splitpoints[roundoff(seg.end)]["out"] if o.windingNumber < 2]
        splitpoints[roundoff(seg.end)]["out"].sort(key = lambda x: x.tangentAtTime(0).angle-inAngle)
        seg = splitpoints[roundoff(seg.end)]["out"].pop(-1)
        # seg = seg.next
        # print("I chose %s\n" % seg)
      else:
        seg = seg.next

    self.activeRepresentation = SegmentRepresentation(self,newsegs)