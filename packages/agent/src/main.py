from packages.agent.src.agent.memoryhelper.memoryhelper import MemoryHelper

def main():
    mem_helper = MemoryHelper()
    if not mem_helper.attach("level1easy.exe"):
        print(f"Failed to attach to the target process! {mem_helper.get_last_error()}")
        return
    array = mem_helper.collect_regions()
    print(f"Collected {array.len} regions")
    
    mem_helper.disassemble_regions(array)


if __name__ == "__main__":
    main()
