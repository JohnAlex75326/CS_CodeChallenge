def jumps(flagHeight, bigJump):
    bigJumpCount = flagHeight // bigJump
    remainingHeight = flagHeight % bigJump
    # Total jumps = big jumps + all needed 1-jumps
    return bigJumpCount + remainingHeight

if __name__ == "__main__":
    import sys
    flagHeight = int(sys.stdin.readline())
    bigJump = int(sys.stdin.readline())
    print(jumps(flagHeight, bigJump))