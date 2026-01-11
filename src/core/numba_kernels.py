
import numpy as np
from numba import jit

@jit(nopython=True, cache=True)
def ask_modulate(bits, time, omega):
    n = len(time)
    result = np.empty(n, dtype=np.float64)
    # We assume scalar omega for ASK as carrier freq is usually constant
    for i in range(n):
        amp = 1.0 if bits[i] > 0.5 else 0.0
        result[i] = amp * np.sin(omega * time[i])
    return result

@jit(nopython=True, cache=True)
def fsk_modulate(bits, time, omega0, omega1):
    n = len(time)
    result = np.empty(n, dtype=np.float64)
    for i in range(n):
        w = omega1 if bits[i] > 0.5 else omega0
        result[i] = np.sin(w * time[i])
    return result

@jit(nopython=True, cache=True)
def psk_modulate(bits, time, omega):
    n = len(time)
    result = np.empty(n, dtype=np.float64)
    pi = np.pi
    for i in range(n):
        phase = 0.0 if bits[i] > 0.5 else pi
        result[i] = np.sin(omega * time[i] + phase)
    return result

@jit(nopython=True, cache=True)
def am_modulate(message, time, omega, modulation_index):
    # envelope = 1.0 + m * message
    # result = envelope * cos(omega * time)
    return (1.0 + modulation_index * message) * np.cos(omega * time)

@jit(nopython=True, cache=True)
def fm_modulate(message, time, carrier_freq, freq_deviation, last_phase, last_time):
    # This maintains state (integral), so it's trickier to vectorize purely.
    # However, Numba handles loops very fast.
    n = len(time)
    result = np.empty(n, dtype=np.float64)
    
    current_phase = last_phase
    prev_t = last_time
    
    two_pi = 2 * np.pi
    
    for i in range(n):
        t = time[i]
        dt = t - prev_t
        if dt > 0:
            inst_freq = carrier_freq + freq_deviation * message[i]
            current_phase += two_pi * inst_freq * dt
        
        result[i] = np.cos(current_phase)
        prev_t = t
        
    return result, current_phase, prev_t

@jit(nopython=True, cache=True)
def pm_modulate(message, time, omega, phase_deviation):
    # phase = omega * time + kp * message
    return np.cos(omega * time + phase_deviation * message)

# --- Demodulation Kernels ---

@jit(nopython=True, cache=True)
def am_demodulate_kernel(signal, alpha, mod_index, prev_envelope):
    n = len(signal)
    output = np.empty(n, dtype=np.float64)
    envelope = prev_envelope
    
    for i in range(n):
        inp = np.abs(signal[i])
        envelope = alpha * inp + (1.0 - alpha) * envelope
        output[i] = (envelope - 1.0) / mod_index
        
    return output, envelope


@jit(nopython=True, cache=True)
def ask_demodulate_kernel(signal, time, bit_duration, 
                          last_bit_index, accumulator, sample_count, current_decoded_val):
    n = len(signal)
    output = np.empty(n, dtype=np.float64)
    
    curr_acc = accumulator
    curr_count = sample_count
    curr_last_idx = last_bit_index
    val = current_decoded_val 
    
    for i in range(n):
        bit_index = int((time[i] + 1e-9) / bit_duration)
        
        if bit_index > curr_last_idx:
            # Decide for previous bit
            if curr_count > 0:
                avg = curr_acc / curr_count
                val = 1.0 if avg > 0.25 else 0.0 # Lower threshold slightly
            
            curr_acc = 0.0
            curr_count = 0
            curr_last_idx = bit_index
            
        curr_acc += np.abs(signal[i])
        curr_count += 1
        output[i] = val
        
    return output, curr_last_idx, curr_acc, curr_count, val

@jit(nopython=True, cache=True)
def fm_demodulate_kernel(signal, time, carrier_freq, dev, 
                         prev_val, last_crossing, alpha, smoothed_val, last_inst_freq):
    n = len(signal)
    output = np.empty(n, dtype=np.float64)
    
    p_val = prev_val
    l_cross = last_crossing
    smooth = smoothed_val
    inst_f = last_inst_freq
    
    for i in range(n):
        curr = signal[i]
        
        # Zero crossing detection: rising edge?
        # Original: if self.prev_value <= 0 < current:
        if p_val <= 0 and curr > 0:
            if l_cross > 0:
                period = time[i] - l_cross
                if period > 0:
                    inst_f = 1.0 / period
            l_cross = time[i]
            
        freq_offset = inst_f - carrier_freq
        normalized = freq_offset / dev
        
        smooth = alpha * normalized + (1.0 - alpha) * smooth
        
        p_val = curr
        output[i] = smooth
        
    return output, p_val, l_cross, smooth, inst_f

# --- Digital Encoder Kernels ---

@jit(nopython=True, cache=True)
def nrz_l_kernel(signal, high, low):
    # NRZ-L: 0 -> high, 1 -> low (based on original code logic which was inverted?)
    # Original: inp > 0.5 (logic 1) -> low_level, else high_level
    n = len(signal)
    output = np.empty(n, dtype=np.float64)
    for i in range(n):
        output[i] = low if signal[i] > 0.5 else high
    return output

@jit(nopython=True, cache=True)
def nrzi_kernel(time, input_signal, rate, high, low, 
                current_level, last_bit_index):
    # Fixed NRZI: Standard USB/HDLC uses NRZI-S (Space/Zero causes transition)
    # 0 -> Transition, 1 -> No Transition
    n = len(time)
    output = np.empty(n, dtype=np.float64)
    
    level = current_level
    last_idx = last_bit_index
    
    for i in range(n):
        bit_idx = int(time[i] * rate + 1e-9) # Epsilon for stability
        
        if bit_idx > last_idx:
            # Check for transition on 0
            is_logic_1 = input_signal[i] > 0.5
            if not is_logic_1: # Logic 0 -> Toggle
                level = high if level == low else low
            last_idx = bit_idx
            
        output[i] = level
        
    return output, level, last_idx

@jit(nopython=True, cache=True)
def manchester_kernel(time, input_signal, bit_duration, half_duration):
    n = len(time)
    output = np.empty(n, dtype=np.float64)
    
    for i in range(n):
        # Add epsilon to time to avoid floating point wrapping at exact boundaries
        t = time[i] + 1e-9
        is_logic_1 = input_signal[i] > 0.5
        
        # Manchester IEEE 802.3: 1 = Low->High, 0 = High->Low
        # First half: 1->Low (-1), 0->High (1)
        
        cycle_pos = t % bit_duration
        is_first_half = cycle_pos < half_duration
        
        if is_logic_1:
            val = -1.0 if is_first_half else 1.0
        else:
            val = 1.0 if is_first_half else -1.0
            
        output[i] = val
    return output

@jit(nopython=True, cache=True)
def ami_kernel(time, input_signal, rate, last_polarity, last_bit_index, current_holding_val):
    n = len(time)
    output = np.empty(n, dtype=np.float64)
    
    polarity = last_polarity
    last_idx = last_bit_index
    curr_val = current_holding_val
    
    for i in range(n):
        bit_idx = int(time[i] * rate)
        
        if bit_idx > last_idx:
            # New bit
            is_logic_1 = input_signal[i] > 0.5
            if is_logic_1:
                # Flip polarity
                curr_val = -polarity
                polarity = curr_val
            else:
                curr_val = 0.0
            last_idx = bit_idx
            
        output[i] = curr_val
        
    return output, polarity, last_idx, curr_val

@jit(nopython=True, cache=True)
def pseudoternary_kernel(time, input_signal, rate, last_polarity, last_bit_index, current_holding_val):
    n = len(time)
    output = np.empty(n, dtype=np.float64)
    
    polarity = last_polarity
    last_idx = last_bit_index
    curr_val = current_holding_val
    
    for i in range(n):
        bit_idx = int(time[i] * rate)
        
        if bit_idx > last_idx:
            is_logic_1 = input_signal[i] > 0.5
            if not is_logic_1: # Logic 0 triggers flip
                curr_val = -polarity
                polarity = curr_val
            else:
                curr_val = 0.0
            last_idx = bit_idx
            
        output[i] = curr_val
        
    return output, polarity, last_idx, curr_val

@jit(nopython=True, cache=True)
def diff_manchester_kernel(time, input_signal, rate, bit_duration, half_duration,
                           prev_end_level, last_bit_index, current_start_level):
    # Rewritten Differential Manchester (IEEE 802.5 Token Ring)
    # Always transition at middle of bit interval.
    # 0 bit: Transition at start.
    # 1 bit: No transition at start.
    
    n = len(time)
    output = np.empty(n, dtype=np.float64)
    
    p_end = prev_end_level
    curr_start = current_start_level
    last_idx = last_bit_index
    
    for i in range(n):
        t = time[i] + 1e-9
        bit_idx = int(t * rate)
        
        if bit_idx > last_idx:
            is_logic_1 = input_signal[i] > 0.5
            
            # Logic 1: No transition at start -> curr_start same as p_end
            # Logic 0: Transition at start -> curr_start flipped p_end
            if is_logic_1:
                curr_start = p_end
            else:
                curr_start = -p_end if p_end != 0 else 1.0 # Handle init case
                if p_end == 0: curr_start = 1.0 # Default start
                
            last_idx = bit_idx

        # Generate waveform
        # First half holds curr_start
        # Second half holds -curr_start (always transition in middle)
        cycle_pos = t % bit_duration
        if cycle_pos < half_duration:
            val = curr_start
        else:
            val = -curr_start
            
        output[i] = val
        p_end = val # Track end level
        
    return output, p_end, last_idx, curr_start


# --- Analog-Digital Kernels ---

@jit(nopython=True, cache=True)
def pcm_encode_kernel(time, input_signal, sample_rate, bit_rate, 
                      n_bits, v_min, v_range_inv, n_levels_m1,
                      last_sample_index, current_code):
    n = len(time)
    output = np.empty(n, dtype=np.float64)
    
    last_idx = last_sample_index
    code = current_code
    sample_period = 1.0 / sample_rate
    
    for i in range(n):
        t = time[i]
        sample_idx = int(t * sample_rate)
        
        if sample_idx > last_idx:
            # New sample period: Sample and Quantize
            val = input_signal[i]
            if val < v_min: val = v_min
            # We don't have v_max here but v_range_inv handles scale
            # Assuming v_max is implied by v_range_inv calculation
            
            norm = (val - v_min) * v_range_inv
            if norm > 1.0: norm = 1.0
            
            code = int(norm * n_levels_m1)
            last_idx = sample_idx
            
        # Serialize
        time_in_sample = t % sample_period
        bit_idx = int(time_in_sample * bit_rate)
        if bit_idx >= n_bits: bit_idx = n_bits - 1
        
        # Bits are usually MSB first
        bit_pos = n_bits - 1 - bit_idx
        bit_val = (code >> bit_pos) & 1
        output[i] = float(bit_val)
        
    return output, last_idx, code

@jit(nopython=True, cache=True)
def delta_encode_kernel(time, input_signal, sample_rate, step_size,
                        last_sample_index, approximation, current_bit):
    n = len(time)
    output = np.empty(n, dtype=np.float64)
    
    last_idx = last_sample_index
    approx = approximation
    bit = current_bit
    
    for i in range(n):
        sample_idx = int(time[i] * sample_rate)
        
        if sample_idx > last_idx:
            inp = input_signal[i]
            if inp > approx:
                bit = 1.0
                approx += step_size
            else:
                bit = 0.0
                approx -= step_size
            last_idx = sample_idx
            
        output[i] = bit
        
    return output, last_idx, approx, bit

@jit(nopython=True, cache=True)
def delta_decode_kernel(time, input_signal, sample_rate, step_size,
                        last_sample_index, approximation):
    n = len(time)
    output = np.empty(n, dtype=np.float64)
    
    last_idx = last_sample_index
    approx = approximation
    
    for i in range(n):
        sample_idx = int(time[i] * sample_rate)
        
        if sample_idx > last_idx:
            bit = input_signal[i]
            # 1 -> up, 0 -> down
            if bit > 0.5:
                approx += step_size
            else:
                approx -= step_size
            last_idx = sample_idx
            
        output[i] = approx
        
    return output, last_idx, approx

@jit(nopython=True, cache=True)
def pcm_decode_kernel(time, input_signal, bit_rate, n_bits,
                      v_min, step_size,
                      last_bit_index, assembly_reg, bits_collected, current_output):
    n = len(time)
    output = np.empty(n, dtype=np.float64)
    
    last_idx = last_bit_index
    reg = assembly_reg
    count = bits_collected
    out_val = current_output
    
    for i in range(n):
        # Robust bit indexing with epsilon
        bit_idx = int((time[i] + 1e-9) * bit_rate)
        
        if bit_idx > last_idx:
            # Sample bit at the *start* of the bit period (or middle?)
            # Ideally middle, but signal should be stable.
            # Assuming digital input 0/1.
            
            bit = 1 if input_signal[i] > 0.5 else 0
            
            # Shift in (MSB first)
            reg = (reg << 1) | bit
            count += 1
            
            if count == n_bits:
                out_val = v_min + reg * step_size
                reg = 0
                count = 0
            
            last_idx = bit_idx
            
        output[i] = out_val
        
    return output, last_idx, reg, count, out_val

@jit(nopython=True, cache=True)
def fsk_demodulate_kernel(time, input_signal, bit_duration, threshold,
                          last_bit_index, last_val, zero_crossings):
    n = len(time)
    output = np.empty(n, dtype=np.float64)
    
    last_idx = last_bit_index
    l_val = last_val
    z_cross = zero_crossings
    decoded_bit = 0.0 # holding val
    
    for i in range(n):
        bit_idx = int(time[i] / bit_duration)
        
        if bit_idx > last_idx:
            # End of bit period, make decision based on counts
            # Note: This simple logic decides for the *just finished* bit.
            # But we need to output something for the *current* sample?
            # The original logic outputs the decision for the PREVIOUS bit during the CURRENT bit.
            
            if last_idx >= 0:
                est_freq = z_cross / (2.0 * bit_duration)
                decoded_bit = 1.0 if est_freq > threshold else 0.0
            
            z_cross = 0
            last_idx = bit_idx
            
        curr = input_signal[i]
        if l_val * curr < 0: # Zero crossing
             z_cross += 1
        l_val = curr
        
        output[i] = decoded_bit
        
    return output, last_idx, l_val, z_cross, decoded_bit

# --- Digital Decoder Kernels ---

@jit(nopython=True, cache=True)
def nrz_l_decode_kernel(time, input_signal, high, low):
    # NRZ-L Decoder: high -> 0, low -> 1 (or vice versa depending on mapping)
    # Encoder was: 0 -> high, 1 -> low.
    # So decoding: if val > mid logic 0, else logic 1.
    n = len(time)
    output = np.empty(n, dtype=np.float64)
    mid = (high + low) / 2.0
    
    for i in range(n):
        # Immediate decoding mostly fine for NRZ-L
        # Encoder used: output[i] = low if signal[i] > 0.5 else high
        # signal > 0.5 was logic 1.
        # So logic 1 -> low (e.g. -1). Logic 0 -> high (e.g. 1).
        
        val = input_signal[i]
        # Invert logic: if val near high -> 0, if val near low -> 1
        # high is usually > low.
        if val > mid:
            output[i] = 0.0
        else:
            output[i] = 1.0
            
    return output

@jit(nopython=True, cache=True)
def nrzi_decode_kernel(time, input_signal, rate, high, low, 
                       last_level, last_bit_index, current_decoded_val):
    # Fixed NRZI Decoder
    # Encoder: 0 -> Toggle, 1 -> No Toggle
    # Decoder: Check if current level != last level.
    # If Changed -> 0. If Same -> 1.
    n = len(time)
    output = np.empty(n, dtype=np.float64)
    l_level = last_level
    last_idx = last_bit_index
    val = current_decoded_val
    mid = (high + low) / 2.0
    
    for i in range(n):
        bit_idx = int((time[i] + 1e-9) * rate)
        
        # Determine current binary level (0 or 1 based on voltage)
        curr_level_binary = 1 if input_signal[i] > mid else 0
        
        if bit_idx > last_idx:
            # New bit period. 
            # If this is the FIRST bit (last_idx == -1), we can't detect change easily.
            # Assuming standard: Line idles High (1). 
            # If starts High -> No change -> 1. If starts Low -> Change -> 0?
            # Or assume we pass initial state correctly.
            
            if last_idx >= 0:
                if curr_level_binary != l_level:
                    # Level changed -> 0
                    val = 0.0
                else:
                    # Level same -> 1
                    val = 1.0
            
            l_level = curr_level_binary
            last_idx = bit_idx
            
        output[i] = val
        
    return output, l_level, last_idx, val

@jit(nopython=True, cache=True)
def manchester_decode_kernel(time, input_signal, bit_duration, half_duration,
                             last_bit_index, current_decoded_val):
    # Manchester IEEE 802.3: 1 = Low->High, 0 = High->Low
    # Sampling: Look at second half.
    # 1 (Low->High): Second half is High (>0)
    # 0 (High->Low): Second half is Low (<0)
    n = len(time)
    output = np.empty(n, dtype=np.float64)
    last_idx = last_bit_index
    val = current_decoded_val
    
    for i in range(n):
        t = time[i] + 1e-9
        bit_idx = int(t / bit_duration)
        cycle_pos = t % bit_duration
        
        if bit_idx > last_idx:
             # Just hold previous value until we reach decision point
             last_idx = bit_idx
        
        # Decision point: 75% of bit duration
        if cycle_pos >= (bit_duration * 0.70):
             if input_signal[i] > 0:
                 val = 1.0
             else:
                 val = 0.0
                 
        output[i] = val
        
    return output, last_idx, val

@jit(nopython=True, cache=True)
def ami_decode_kernel(time, input_signal, rate, last_bit_index, current_decoded_val):
    n = len(time)
    output = np.empty(n, dtype=np.float64)
    last_idx = last_bit_index
    val = current_decoded_val
    
    for i in range(n):
        bit_idx = int(time[i] * rate)
        
        if bit_idx > last_idx:
            inp = np.abs(input_signal[i])
            val = 1.0 if inp > 0.5 else 0.0
            last_idx = bit_idx
            
        output[i] = val
    return output, last_idx, val

@jit(nopython=True, cache=True)
def pseudoternary_decode_kernel(time, input_signal, rate, last_bit_index, current_decoded_val):
    n = len(time)
    output = np.empty(n, dtype=np.float64)
    last_idx = last_bit_index
    val = current_decoded_val
    
    for i in range(n):
        bit_idx = int(time[i] * rate)
        
        if bit_idx > last_idx:
            inp = np.abs(input_signal[i])
            val = 0.0 if inp > 0.5 else 1.0
            last_idx = bit_idx
            
        output[i] = val
    return output, last_idx, val

@jit(nopython=True, cache=True)
def diff_manchester_decode_kernel(time, input_signal, bit_duration, quarter_duration,
                                  last_bit_index, last_end_level, current_decoded_val):
    # Diff Manchester IEEE 802.5:
    # 0 -> Transition at beginning
    # 1 -> No Transition at beginning
    # Always transition at middle.
    
    n = len(time)
    output = np.empty(n, dtype=np.float64)
    last_idx = last_bit_index
    l_end = last_end_level
    val = current_decoded_val
    
    for i in range(n):
        t = time[i] + 1e-9
        bit_idx = int(t / bit_duration)
        cycle_pos = t % bit_duration
        
        curr_level = 1.0 if input_signal[i] > 0 else -1.0
        
        # We need to detect transition at the boundary.
        # But we process sample by sample.
        # Check at 25% mark (start of bit) and compare with previous bit's end.
        
        if bit_idx > last_idx:
            # New bit started.
            # We must wait for first quarter to settle to check level.
            last_idx = bit_idx
            
        if cycle_pos >= (bit_duration * 0.15) and cycle_pos <= (bit_duration * 0.35):
            # Sampling window for Start Level
            # If Start Level == Last End Level -> No Transition -> Logic 1
            # If Start Level != Last End Level -> Transition -> Logic 0
            # Only update if we have history (last_end_level != 0 at start?)
            # Assuming l_end is initialized to something meaningful or we skip first match.
            if l_end != 0: # Avoid initial glitch
                 if curr_level == l_end:
                     val = 1.0
                 else:
                     val = 0.0
        
        # Update Last End Level at 75% mark (after mid-bit transition)
        # This will be the reference for the NEXT bit.
        if cycle_pos >= (bit_duration * 0.75):
            l_end = curr_level
            
        output[i] = val
        
    return output, last_idx, l_end, val

@jit(nopython=True, cache=True)
def psk_demodulate_kernel(time, input_signal, bit_duration, carrier_freq,
                          last_bit_index, accumulator, sample_count, decoded_bit):
    n = len(time)
    output = np.empty(n, dtype=np.float64)
    
    last_idx = last_bit_index
    acc = accumulator
    count = sample_count
    dec_bit = decoded_bit
    omega = 2 * np.pi * carrier_freq
    
    for i in range(n):
        t = time[i]
        bit_idx = int(t / bit_duration)
        
        if bit_idx > last_idx:
            if count > 0:
                avg = acc / count
                # Correlator output > 0 means phase 0 (logic 1?), < 0 means phase 180 (logic 0)
                # Depends on mapping. Let's assume standard BPSK: 1=>0deg, 0=>180deg
                # cos(wt) * cos(wt) > 0. cos(wt + pi) * cos(wt) < 0.
                if avg > 0:
                    dec_bit = 1.0
                else: 
                    dec_bit = 0.0
            
            acc = 0.0
            count = 0
            last_idx = bit_idx
            
        ref = np.sin(omega * t) # Original code uses sin? usually cos for BPSK unless carrier is sin
        # Original: ref = math.sin(2 * math.pi * self.carrier_freq * time)
        # We stick to original behavior for phase alignment.
        
        acc += input_signal[i] * ref
        count += 1
        
        output[i] = dec_bit
        
    return output, last_idx, acc, count, dec_bit
