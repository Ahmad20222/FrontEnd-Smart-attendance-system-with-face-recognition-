"""
Enrollment Service Module

This module provides a standalone service for capturing images from a camera
for face enrollment. It can run in both GUI and headless modes.

Used as a subprocess by the attendance router to capture enrollment images.
"""

import os
import sys
import time
from pathlib import Path

import cv2


def main(out_dir: str, cam_index: int = 0, timeout_ms: int = 15000):
    """
    Main function to capture 10 images from camera for enrollment.
    
    Opens camera, stabilizes it, then captures 10 images with quality enhancement.
    Can run in GUI mode (shows preview window) or headless mode (automatic capture).
    
    Args:
        out_dir: Output directory path to save captured images
        cam_index: Camera index (default: 0)
        timeout_ms: Timeout in milliseconds (default: 15000)
        
    Exit codes:
        0: Success
        2: Camera cannot be opened
        3: No images were saved
        4: Failed to save an image
    """
    print(f"INFO: Enrollment service started", file=sys.stderr)
    print(f"INFO: Output directory: {out_dir}", file=sys.stderr)
    print(f"INFO: Camera index: {cam_index}", file=sys.stderr)
    print(f"INFO: Timeout: {timeout_ms}ms", file=sys.stderr)
    
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"INFO: Output directory created/exists: {out_dir.exists()}", file=sys.stderr)

    print(f"INFO: Attempting to open camera {cam_index}", file=sys.stderr)
    cap = cv2.VideoCapture(cam_index)
    if not cap.isOpened():
        error_msg = f"ERR: Cannot open camera {cam_index}"
        print(error_msg, file=sys.stderr)
        sys.exit(2)
    
    # Set camera properties for better quality
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)
    
    # Allow camera to stabilize
    print(f"INFO: Camera {cam_index} opened successfully, allowing stabilization...", file=sys.stderr)
    for _ in range(10):  # Read and discard first 10 frames for stabilization
        cap.read()
    print(f"INFO: Camera stabilized", file=sys.stderr)

    # Try to create GUI window, but continue in headless mode if it fails
    title = "Enroll - Press SPACE to start capturing (Q to quit)"
    has_gui = False
    print(f"INFO: Attempting to create GUI window", file=sys.stderr)
    try:
        cv2.namedWindow(title, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(title, 900, 600)
        has_gui = True
        print(f"INFO: GUI window created successfully - running in GUI mode", file=sys.stderr)
    except Exception as e:
        print(f"INFO: GUI not available - running in headless mode: {str(e)}", file=sys.stderr)
        has_gui = False

    start_time = time.time()
    saved = 0
    last_save_time = 0.0
    started = False
    frames_read = 0
    frames_failed = 0
    last_countdown_printed = -1  # Track last countdown number printed
    
    # In headless mode, start capturing after a delay to allow user to position themselves
    if not has_gui:
        wait_time = 3.0  # Wait 3 seconds for user to position
        print(f"INFO: Headless mode - will start capturing automatically after {wait_time} seconds", file=sys.stderr)
        print(f"INFO: Please position yourself in front of the camera now", file=sys.stderr)
        auto_start_time = time.time() + wait_time

    print(f"INFO: Starting capture loop (GUI mode: {has_gui})", file=sys.stderr)
    while True:
        ok, frame = cap.read()
        frames_read += 1
        
        if not ok:
            frames_failed += 1
            elapsed = (time.time() - start_time) * 1000
            if elapsed > timeout_ms:
                print(f"WARN: Timeout reached ({elapsed:.0f}ms > {timeout_ms}ms), breaking loop", file=sys.stderr)
                break
            if has_gui:
                cv2.waitKey(1)
            else:
                time.sleep(0.01)  # Small delay in headless mode
            continue

        now = time.time()
        
        # Auto-start in headless mode after delay with countdown
        if not has_gui and not started:
            remaining = auto_start_time - now
            if remaining > 0:
                # Print countdown every second
                countdown_sec = int(remaining) + 1
                if countdown_sec != last_countdown_printed and countdown_sec <= int(wait_time):
                    print(f"INFO: Starting capture in {countdown_sec} second(s)...", file=sys.stderr)
                    last_countdown_printed = countdown_sec
            elif now >= auto_start_time:
                started = True
                print(f"INFO: Starting automatic capture - Please keep still and look at the camera!", file=sys.stderr)
        
        # Save frames with improved timing and quality checks
        if started and saved < 10 and (now - last_save_time) > 0.8:  # Increased interval to 0.8 seconds
            # Enhance image quality before saving
            enhanced_frame = frame.copy()
            
            # Apply basic image enhancements
            # Convert to LAB color space for better lighting adjustment
            lab = cv2.cvtColor(enhanced_frame, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            
            # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization) to L channel
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            l = clahe.apply(l)
            
            # Merge channels and convert back to BGR
            enhanced_frame = cv2.merge([l, a, b])
            enhanced_frame = cv2.cvtColor(enhanced_frame, cv2.COLOR_LAB2BGR)
            
            filename = out_dir / f"frame_{saved + 1}.png"
            print(f"INFO: Saving frame {saved + 1}/10 to {filename.name}", file=sys.stderr)
            ok = cv2.imwrite(str(filename), enhanced_frame, [cv2.IMWRITE_PNG_COMPRESSION, 1])
            if not ok:
                error_msg = f"ERR: Failed to save image {filename.name}"
                print(error_msg, file=sys.stderr)
                cap.release()
                if has_gui:
                    try:
                        cv2.destroyAllWindows()
                    except:
                        pass
                sys.exit(4)
            saved += 1
            last_save_time = now
            print(f"INFO: Successfully saved frame {saved}/10", file=sys.stderr)

        # GUI display (only if GUI is available)
        if has_gui:
            try:
                if started:
                    cv2.putText(frame, f"Saved: {saved}/10 (Q to quit)",
                                (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                else:
                    cv2.putText(frame, "Press SPACE to start capturing (Q to quit)",
                                (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                cv2.imshow(title, frame)
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord(' '):
                    if not started:
                        started = True
                        print(f"INFO: Capture started by user (SPACE pressed)", file=sys.stderr)
                elif key in (ord('q'), ord('Q')):
                    print(f"INFO: Capture stopped by user (Q pressed)", file=sys.stderr)
                    break
            except Exception as e:
                print(f"WARN: GUI display error: {str(e)}", file=sys.stderr)
                # Fallback to headless mode
                has_gui = False
                if not started:
                    started = True
                    print(f"INFO: Switching to headless mode and auto-starting", file=sys.stderr)
            
        if saved >= 10:
            print(f"INFO: Target reached (10 frames saved), stopping", file=sys.stderr)
            break
        if (time.time() - start_time) * 1000 > timeout_ms:
            print(f"WARN: Timeout reached, stopping", file=sys.stderr)
            break

    print(f"INFO: Capture loop ended. Frames read: {frames_read}, Failed: {frames_failed}, Saved: {saved}", file=sys.stderr)
    cap.release()
    print(f"INFO: Camera released", file=sys.stderr)
    
    if has_gui:
        try:
            cv2.destroyAllWindows()
            print(f"INFO: GUI windows destroyed", file=sys.stderr)
        except Exception as e:
            print(f"WARN: Error destroying windows: {str(e)}", file=sys.stderr)

    if saved == 0:
        error_msg = f"ERR: No images were saved (frames_read={frames_read}, frames_failed={frames_failed})"
        print(error_msg, file=sys.stderr)
        sys.exit(3)
    
    print(f"INFO: Enrollment service completed successfully. Saved {saved} image(s)", file=sys.stderr)

if __name__ == "__main__":
    out_dir = sys.argv[1]
    cam_index = int(sys.argv[2]) if len(sys.argv) >= 3 else 0
    timeout_ms = int(sys.argv[3]) if len(sys.argv) >= 4 else 15000
    os.makedirs(out_dir, exist_ok=True)
    main(out_dir, cam_index, timeout_ms)
