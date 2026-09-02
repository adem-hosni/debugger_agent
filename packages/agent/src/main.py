from memoryhelper.memoryhelper import MemoryHelper
from agents.orchestrator import OrchestratorAgent

def main():
    agent = OrchestratorAgent()
    agent.bind("level1easy.exe")
    agent.map_functions()
    agent.debug_assembly()
    # print(agent.function_map.find_node("00007FF627C82250"))
    print("Completed!")


if __name__ == "__main__":
    main()
