from typing import List
from task import Task
from collections import deque
import heapq

class GanttObject:
    def __init__(self, pid, start, end = None):
        self.pid = pid
        self.start = start
        self.end = end

    def to_dict(self):
        return {
            "pid": self.pid,
            "start": self.start,
            "end": self.end
        }

    def __repr__(self):
        return f"GanttObject(pid={self.pid}, start={self.start}, end={self.end})"

class Scheduler:
    def __init__(self, policy, jobs, quantum=0):
        self.policy: str = policy
        self.jobs: List[Task] = jobs
        self.quantum: int = quantum

    def schedule(self):
        policy = self.policy.upper()

        if policy == "FIFO":
            return self.fifo()
        elif policy == "SJF":
            return self.sjf()
        elif policy == "RR":
            return self.round_robin()
        elif policy == "PRIORITY":
            return self.priority()
        else:
            raise ValueError(f"Unsupported scheduling policy: {self.policy}")

    def round_robin(self) -> List[GanttObject]:
        inactive_task_queue = deque(sorted(self.jobs, key=lambda task: (task.arrival, task.pid)))
        active_task_queue = deque()
        time = 0
        gantt_timeline: List[GanttObject] = []

        while active_task_queue or inactive_task_queue:
            if not active_task_queue:
                active_task_queue.append(inactive_task_queue.popleft())

            task_to_run: Task = active_task_queue.popleft()
            time_start = max(task_to_run.arrival, time)

            if task_to_run.start_time is None:
                task_to_run.start_time = time_start
        
            time_for_job = min(self.quantum, task_to_run.remaining)
            time = time_start + time_for_job
            task_to_run.remaining -= time_for_job

            earlier_arrivals = []
            while inactive_task_queue and time > inactive_task_queue[0].arrival:
                earlier_arrivals.append(inactive_task_queue.popleft())
            
            boundary_arrivals = []
            #Logic to break lexicographical ties if we need to readd a task back at the same time we need to add the current task
            while inactive_task_queue and inactive_task_queue[0].arrival == time:
                boundary_arrivals.append(inactive_task_queue.popleft())

            if task_to_run.remaining == 0:
                task_to_run.finish_time = time
            else:
                boundary_arrivals.append(task_to_run)
            
            active_task_queue.extend(earlier_arrivals)
            active_task_queue.extend(sorted(boundary_arrivals, key=lambda task: task.pid))
            gantt_timeline.append(GanttObject(task_to_run.pid, time_start, time))
        
        return gantt_timeline


# recall fifo (first-in first out): basic heap -> upon task arrival time, non pre-emptive
    def fifo(self) -> List[GanttObject]:
        min_heap = [(task.arrival, task.burst, task.pid) for task in self.jobs]
        pid_task_dict = {task.pid: task for task in self.jobs}
        heapq.heapify(min_heap)

        curr_time = 0
        gantt_timeline: List[GanttObject] = []
        while min_heap:
            arrival_t, task_length, curr_task_pid = heapq.heappop(min_heap) # Popping off earliest task
            start_time = max(curr_time, arrival_t)
            end_time = start_time + task_length

            task = pid_task_dict[curr_task_pid]  # Task Stats updating (whoever is implementing that, i can as well)
            task.start_time = start_time
            task.finish_time = end_time

            gantt_timeline.append(GanttObject(curr_task_pid, start_time, end_time))  # timeline building
            curr_time = end_time

        return gantt_timeline

        

    def sjf(self):
        raise NotImplementedError
    
    #Chooses highest priority process instead of smallest length to determine next run
    def priority(self):
        raise NotImplementedError
    
    #OPTIONAL to ensure full marks would probably be fun
    def MLFQ(self):
        pass
