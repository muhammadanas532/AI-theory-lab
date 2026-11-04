class ClassroomAgent:
    def __init__(self):
        self.previous_mode = None

    def act(self, temp, occupied):
        if not occupied:
            target_mode = "ECO"
        elif temp > 26:
            target_mode = "COOL"
        elif temp < 20:
            target_mode = "WARM"
        else:
            target_mode = "IDLE"

        send_command = (target_mode != self.previous_mode)
        old_mode = self.previous_mode
        self.previous_mode = target_mode
        return old_mode, target_mode, send_command


if __name__ == "__main__":
    agent = ClassroomAgent()
    percepts = [
        (29, True),
        (29, True),
        (20, True),
        (26, True),
        (19, True),
        (29, False),
        (20, False),
        (25, True)
    ]

    for step, (temp, occupied) in enumerate(percepts, 1):
        prev_mode, target_mode, send_command = agent.act(temp, occupied)
        action_str = "SEND_COMMAND" if send_command else "NO_COMMAND"
        print(f"Step {step}: Percept=({temp}C, Occupied={occupied}) | Prev={prev_mode} | Target={target_mode} | Action={action_str}")

