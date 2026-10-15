/* Copyright 2024 ~ 2025 @ Keychron (https://www.keychron.com)
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program. If not, see <http://www.gnu.org/licenses/>.
 */

#include "keychron.h"

#ifdef DIP_SWITCH_ENABLE
bool dip_switch_update_kb(uint8_t index, bool active) {
    if (index == 0) {
        default_layer_set(1UL << (active ? 2 : 0));
    }
    dip_switch_update_user(index, active);

    return true;
}
#endif

void keyboard_post_init_kb(void) {
    keychron_common_init();
    keyboard_post_init_user();
}

#ifdef LK_WIRELESS_ENABLE
bool lpm_is_kb_idle(void) {
    return !backlight_indicator_is_active();
}

#    include "keychron_raw_hid.h"

#    ifndef BATTERY_PUSH_INTERVAL
#        define BATTERY_PUSH_INTERVAL 2000
#    endif

static uint32_t battery_push_timer = 0;

/* The 2.4 GHz receiver does not forward host -> keyboard raw HID requests,
 * so push the KC_GET_BATTERY report to the host periodically while connected. */
void keychron_task_kb(void) {
    if (timer_elapsed32(battery_push_timer) > BATTERY_PUSH_INTERVAL) {
        battery_push_timer = timer_read32();
        if ((get_transport() & TRANSPORT_WIRELESS) && wireless_get_state() == WT_CONNECTED) {
            kc_battery_push();
        }
    }
}
#endif
