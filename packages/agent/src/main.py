from memoryhelper.memoryhelper import MemoryHelper
from agents.orchestrator import OrchestratorAgent

def main():
    agent = OrchestratorAgent()
    agent.bind("level1easy.exe")
    agent.map_functions()
    print("Completed!")


if __name__ == "__main__":
    main()
