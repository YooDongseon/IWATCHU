import Wearos
import Tizenos_app
import Tizenos_debug
import Watchos
import sys

if __name__ == "__main__":                                                                                                                      # 프로그램 메인
    if sys.argv[1] == "Wear":
        Wearos.main()
        
    elif sys.argv[1] == "Tizen":
        if sys.argv[2] == "app":
            Tizenos_app.main(sys.argv[3])
        
        elif sys.argv[2] == "debug":
            Tizenos_debug.main(sys.argv[3])
        
        else :
            print("Check parameters first Or Look at the manual")
    
    elif sys.argv[1] == "Watch":
        Watchos.main(sys.argv[2])
        
    else :
        print("Check parameters first Or Look at the manual")