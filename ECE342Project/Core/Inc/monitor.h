/*
 * monitor.h
 *
 *  Created on: Mar 8, 2026
 *      Author: shuja
 */
#include <string.h>

#ifndef INC_MONITOR_H_
#define INC_MONITOR_H_

#define IMG_COL 320
#define IMG_ROW 180

#define IMG_COL_2 IMG_COL/2
#define IMG_SIZE IMG_ROW * IMG_COL_2

// pack 2 pixels into one byte, 4 bits each
typedef struct
{
  uint8_t p1 : 4;
  uint8_t p2 : 4;
} pix2;

// one entire frame
typedef struct
{
  pix2 data[IMG_SIZE]; // 2 pixels per byte so /2
} frame;

typedef enum
{
    BLACK          = 0x1,
    BLUE           = 0x2,
    GREEN          = 0x3,
    CYAN           = 0x4,
    RED            = 0x5,
    MAGENTA        = 0x6,
    BROWN          = 0x7,
    LIGHTGRAY      = 0x8,
    DARKGRAY       = 0x9,
    LIGHTBLUE      = 0xA,
    LIGHTGREEN     = 0xB,
    LIGHTCYAN      = 0xC,
    LIGHTRED       = 0xD,
    LIGHTMAGENTA   = 0xE,
    WHITE          = 0xF
} pixel_color;

static inline void write_pixel(frame *f, uint16_t x, uint16_t y, uint8_t value)
{
  value &= 0xF;  // get 4 lsb

  uint16_t x_index = x >> 1;          // x / 2
  uint32_t idx = (y * IMG_COL_2) + x_index;

  if (x & 1)
  {
      f->data[idx].p2 = value;        // odd pixel
  } else
  {
      f->data[idx].p1 = value;        // even pixel
  }
}

static inline void clear_frame(frame *f, uint8_t value)
{
    uint8_t both_pixels = (value << 4) | value;  // set both pixels in pix2
    memset(f->data, both_pixels, sizeof(f->data));
}

void uart_send_bin(UART_HandleTypeDef *huart3, uint8_t *buff, unsigned int len)
{
  HAL_UART_Transmit(huart3, (uint8_t *)buff, len, 1000);
}

#endif /* INC_MONITOR_H_ */
