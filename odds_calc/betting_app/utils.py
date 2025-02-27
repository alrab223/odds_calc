def assign_frames(total):
   groups = []
   base = total // 8
   rem = total % 8
   current = 1
   for frame in range(1, 9):
      size = base + (1 if frame > 8 - rem else 0)
      groups.append((frame, current, current + size - 1))
      current += size
   return groups

def get_frame_for_horse(horse, total):
   groups = assign_frames(total)
   for frame, start, end in groups:
      if start <= horse <= end:
         return frame
   return None
