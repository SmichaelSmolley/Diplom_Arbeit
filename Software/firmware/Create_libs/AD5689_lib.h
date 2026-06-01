#include <stdint.h>



#define CMD_WRITE_TO_INPUT_REG          0b0001	//dependent on LDAC input
#define CMD_UPDATE_DAC_WITH_INPUT_REG   0b0010
#define CMD_WRITE_AND_UPDATE_DAC        0b0011
#define CMD_POWER_UP_DOWN_DAC           0b0100
#define CMD_HARDWARE_LDAC_MASK          0b0101
#define CMD_SOFWARE_RESET               0b0110
#define CMD_REFERENCE_SOURCE            0b0111
#define CMD_DAISY_CHAIN_ENABLE          0b1000
#define CMD_READBACK_ENABLE             0b1001
#define ADDR_DAC_A                      0b0001
#define ADDR_DAC_B                      0b1000
#define ADDR_DAC_AB                     0b1001