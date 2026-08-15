from memoryhelper.memoryhelper import MemoryHelper

def main():
    mem_helper = MemoryHelper()
    if not mem_helper.attach("level1easy.exe"):
        print(f"Failed to attach to the target process! {mem_helper.get_last_error()}")
        return
    print(mem_helper.build_funcmap())


if __name__ == "__main__":
    main()
