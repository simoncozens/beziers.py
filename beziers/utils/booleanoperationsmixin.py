import sys
from beziers.path.representations.Segment import SegmentRepresentation
from beziers.utils.intersectionsmixin import Intersection

class BooleanOperationsMixin:

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

  def clip(self,clip,s_entry,c_entry):
    splitlist1 = []
    splitlist2 = []
    intersections = {}
    cloned = self.clone()
    clip = clip.clone()

    for s1 in self.asSegments():
      for s2 in clip.asSegments():
        for i in s1.intersections(s2):
          if i.t1 > 1e-2 and i.t1 < 1-1e-2:
            if i.seg1 == s1:
              splitlist1.append((i.seg1,i.t1))
              splitlist2.append((i.seg2,i.t2))
            else:
              splitlist2.append((i.seg1,i.t1))
              splitlist1.append((i.seg2,i.t2))
            intersections[i.point] = i

    # print("Split list: %s" % splitlist1)
    # print("Split list 2: %s" % splitlist2)
    cloned.splitAtPoints(splitlist1)
    clip.splitAtPoints(splitlist2)
    # print("Self:")
    # print(cloned.asSegments())
    # print("Clip:")
    # print(clip.asSegments())

    # print("List of intersections")
    # for i in intersections.keys(): print(i)
    def markIntersections(segs,toggle):
      for s1 in segs:
        isInter = False
        for i in intersections.keys():
          # print("Intersection %s " % intersections[i].point)
          if i.distanceFrom(s1.start) <= 1:
            # print("Found intersection at %s" % s1.start)
            s1.startIsEntry = toggle
            toggle = not toggle
            isInter = intersections[i]
            break
        s1.startIsIntersection = isInter
      for i in range(0,len(segs)):
        seg = segs[i]
        seg.startIsProcessed = False
        seg.prev = segs[i-1]
        if i < len(segs)-1:
          seg.next = segs[i+1]
        else:
          seg.next = segs[0]

    segs1 = cloned.asSegments()
    segs2 = clip.asSegments()
    s_entry ^= not clip.pointIsInside(segs1[0].start)
    markIntersections(segs1, s_entry)
    c_entry ^= not cloned.pointIsInside(segs2[0].start)
    markIntersections(segs2, c_entry)

    # Find neighbours
    for s1 in segs1:
      if s1.startIsIntersection:
        for s2 in segs2:
          if s2.start.distanceFrom(s1.start) <= 1:
            # print("Intersection in %s " % s1)
            s1.neighbour = s2
            s2.neighbour = s1

    shapes = []
    clipped = []

    def unprocessed(segs):
      for v in segs:
        if v.startIsIntersection and not v.startIsProcessed:
          return True
      return False

    while unprocessed(segs1):
      current = segs1[0]
      while not(current.startIsIntersection) or current.startIsProcessed: current = current.next
      clipped = []
      # print("New shape")
      while True:
        # print("At intersection: %s" % current)
        # print(current, current.startIsProcessed, current.startIsIntersection)
        current.startIsProcessed = True
        if current.startIsIntersection:
          current.neighbour.startIsProcessed = True
        if current.startIsEntry:
          while True:
            clipped.append(current.clone())
            current = current.next
            # print("Adding segment %s" % current)
            if current.startIsIntersection:
              break
        else:
          while True:
            # print("Running backwards")
            current = current.prev
            clipped.append(current.reversed())
            # print("Adding segment %s" % current.reversed())
            if current.startIsIntersection:
              break
        # print("Going to neighbour")
        current = current.neighbour
        if current.startIsProcessed:
          break
      # print("Final shape: %s" % clipped)
      shapes.append(clipped)
    if not shapes:
      return [ self ]
    from beziers.path import BezierPath
    paths = [BezierPath.fromSegments(p) for p in shapes]
    return paths

  def union(self,other):
    """Returns a list of Bezier paths representing the union of the two input paths."""
    return self.clip(other, True, True)

  def intersection(self,other):
    """Returns a list of Bezier paths representing the intersection of the two input paths."""
    return self.clip(other, False, False)

  def difference(self,other):
    """Returns a list of Bezier paths representing the first input path subtracted from the second."""
    return self.clip(other, True, False)
