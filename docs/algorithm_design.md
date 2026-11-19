# CampusFlow AI – Algorithm Design

## 1. Task Prioritization Algorithm

The priority score $P \in [0, 100]$ is computed deterministically in Python using:
$$P = (0.40 \times U) + (0.25 \times I) + (0.20 \times D) + (0.15 \times W)$$

### Factor Normalization ($[0, 100]$):
1. **Urgency Score ($U$):**
   - Overdue or Due Today ($\le 0$ days): $100$
   - $\le 1$ day: $95$
   - $\le 2$ days: $90$
   - $\le 3$ days: $80$
   - $\le 5$ days: $70$
   - $\le 7$ days: $55$
   - $\le 14$ days: $40$
   - $\le 30$ days: $25$
   - $> 30$ days: $10$
   - No deadline: $20$ (baseline)
2. **Importance Score ($I$):** Critical = $95$, Important = $75$, Normal = $50$.
3. **Difficulty Score ($D$):** Difficult = $85$, Medium = $60$, Easy = $35$.
4. **Workload Score ($W$):** $\ge 10$h = $95$, $\ge 6$h = $80$, $\ge 4$h = $65$, $\ge 2$h = $50$, $< 2$h = $30$.

### Thresholds:
- **High Priority:** $P \ge 70.0$
- **Medium Priority:** $40.0 \le P < 70.0$
- **Low Priority:** $P < 40.0$

---

## 2. Conflict Detection Algorithm

Implemented in `backend/app/services/conflict_service.py`:
1. **Study Session Overlap:** Detects if $\text{start}_1 < \text{end}_2 \land \text{start}_2 < \text{end}_1$ on the same calendar date.
2. **Competing Deadlines:** Groups active tasks by target deadline date; flags dates with multiple tasks where cumulative workload exceeds available daily study hours.
3. **Insufficient Preparation Time:** Computes total available hours across student study slots between $\text{now}$ and $\text{deadline}$. If $\text{available\_hours} < \text{workload}$, reports high-severity infeasibility.
4. **College Hours Conflict:** Checks if any scheduled study session falls within the student's college hours ($09:00 - 16:00$).
5. **Outside Student Availability:** Identifies sessions placed on days marked inactive by the student.

---

## 3. Personalized Study Planning Algorithm

Implemented in `backend/app/services/planner_service.py`:
1. Fetch all confirmed, uncompleted tasks for the student.
2. Dynamically re-evaluate priority score $P$ for each task.
3. Sort tasks descending by priority score (high-priority tasks scheduled first).
4. Fetch active study availability intervals and college schedules.
5. Retrieve and preserve all existing sessions marked as `completed`.
6. Break down daily available study windows into discrete blocks ($\text{duration} = 45/60/90$ min) followed by mandatory breaks ($\text{break} = 10/15/20$ min).
7. Allocate slots chronologically prior to each task's submission deadline or event date.
8. If available slots prior to deadline are exhausted, record an infeasibility warning.

---

## 4. Dynamic Rescheduling Algorithm

When a student marks a task delayed or misses a study session:
1. Identify the affected task and its remaining incomplete workload.
2. Delete only the `scheduled` (pending) sessions for that task.
3. Preserve all `completed` study sessions intact.
4. Query available future time slots.
5. Re-run priority-first slot allocation.
6. Record change reason in `schedule_change_history`.
7. Dispatch updated session notifications.
