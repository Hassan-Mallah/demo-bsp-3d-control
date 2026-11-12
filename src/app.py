from flask import Flask, jsonify, send_from_directory
import subprocess
import re
import psutil # Make sure you run: sudo apt install python3-psutil

app = Flask(__name__, static_folder='.')

# Serve the main HTML file (m2.html instead of v2.html)
@app.route('/')
def index():
    return send_from_directory('.', 'm2.html')

# Serve images and other static files
@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('.', path)

# API to read live GPIO data
@app.route('/api/gpio')
def get_gpio():
    try:
        # Use sudo to ensure permission to read hardware
        result = subprocess.run(['sudo', 'gpioinfo'], capture_output=True, text=True, check=True)
        output = result.stdout
        
        consumed_data = {}
        current_chip = None
        
        for line in output.split('\n'):
            chip_match = re.match(r'(gpiochip\d+) - \d+ lines:', line)
            if chip_match:
                current_chip = chip_match.group(1)
                consumed_data[current_chip] = {}
                continue
                
            # Look for lines with a consumer
            line_match = re.match(r'\s+line\s+(\d+):.*consumer=(.*)', line)
            if line_match and current_chip:
                line_num = line_match.group(1)
                consumer = line_match.group(2).strip()
                consumed_data[current_chip][line_num] = consumer
                
        return jsonify(consumed_data)
    except Exception as e:
        print(f"!!! ERROR READING GPIO: {str(e)} !!!")
        return jsonify({"error": str(e)}), 500

# API to read system stats (CPU, RAM, Disk, Temp)
@app.route('/api/system')
def get_system_stats():
    try:
        # Get CPU load (percentage)
        cpu_percent = psutil.cpu_percent(interval=None)
        
        # Get RAM usage
        mem = psutil.virtual_memory()
        ram_percent = mem.percent
        ram_used = round(mem.used / (1024**3), 1) # in GB
        ram_total = round(mem.total / (1024**3), 1) # in GB
        
        # Get Disk/Storage usage (root partition)
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent
        disk_used = round(disk.used / (1024**3), 1) # in GB
        disk_total = round(disk.total / (1024**3), 1) # in GB
        
        # Get CPU temperature (specific to Raspberry Pi / Rockchip)
        try:
            with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
                temp = int(f.read()) / 1000.0
        except:
            temp = 0.0

        return jsonify({
            "cpu": cpu_percent,
            "ram": {"percent": ram_percent, "used": ram_used, "total": ram_total},
            "disk": {"percent": disk_percent, "used": disk_used, "total": disk_total},
            "temp": temp
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("Starting Quectel Pi M2 Dashboard Server...")
    print("Open your browser and go to http://localhost:5050")
    # Run on port 5050 as requested
    app.run(host='0.0.0.0', port=5050, debug=True)
