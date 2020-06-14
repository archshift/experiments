#include <msp430.h>
#include <cstdint>
#include <cassert>
#include <cstdlib>

struct Uart {
    Uart() {
        P3SEL |= 0x08;

        UCA0CTL1 |= UCSWRST;
        UCA0CTL1 |= UCSSEL_1;
        // Baud rate: CLK / 3 = 9600
        UCA0BRW = 3;
        // Modulation settings. TODO: how does this work?
        UCA0MCTL = UCBRS_3 | UCBRF_0;
        UCA0CTL1 &= ~UCSWRST;
    }

    void wait_tx() {
        while (!(UCA0IFG & UCTXIFG));
    }

    void write(char c) {
        wait_tx();
        UCA0TXBUF = c;
    }

    void write(const char *str) {
        char c;
        while ((c = *str++)) {
            if (c == '\n')
                write('\r');
            write(c);
        }
    }

    void write_dec(int i) {
        char buf[12];
        write(itoa(i, buf, 10));
    }
};

struct pin {
    char major : 4;
    char minor : 4;

    pin(char major, char minor) {
        assert(major <= 8);
        assert(minor < 8);
        this->major = major;
        this->minor = minor;
    }
};

struct Rtc {
    Rtc() {
        RTCCTL01 = RTCMODE;
        RTCSEC = 0;
        RTCMIN = 0;
        RTCHOUR = 0;
    }

    void Time(char *secs, char *mins, char *hrs) {
        while (!(RTCCTL01 & RTCRDY));
        *secs = RTCSEC;
        *mins = RTCMIN;
        *hrs = RTCHOUR;
    }
};

template <typename T>
struct Watched {
    T old_val;
    T val;
    bool diff;

    bool take_diff() {
        bool out = diff || old_val != val;
        old_val = val;
        diff = false;
        return out;
    }

    T *operator &() {
        diff |= old_val != val;
        old_val = val;
        return &val;
    }
    operator T() {
        return val;
    }
};

int main() {
    WDTCTL = WDTPW | WDTHOLD;

    Uart uart;
    Rtc rtc;

    for (int i = 0; i < 40; i++)
        uart.write('\n');
    uart.write("Zeroing clock\n");

    Watched<char> sec, min, hr;
    rtc.Time(&sec, &min, &hr);
    sec.take_diff();
    min.take_diff();
    hr.take_diff();

    while (1) {
        rtc.Time(&sec, &min, &hr);

        uart.write("RTC: +");
        uart.write_dec(hr);
        uart.write(":");
        uart.write_dec(min);
        uart.write(":");
        uart.write_dec(sec);
        uart.write("\n");

        if (hr.take_diff()) {
            if (hr == 0) {
                uart.write("Switching light on!\n");
            } else if (hr == 8) {
                uart.write("Switching light off!\n");
            }
        }

        while (!min.take_diff()) {
            rtc.Time(&sec, &min, &hr);
        }
    }
}

