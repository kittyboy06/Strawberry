"""Demonstration catalog and laboratory program fixtures for offline first-run."""

import hashlib

DEMO_PROGRAMS = {
    "socket_server.py": (
        "import socket\n\n"
        "# Create TCP Socket\n"
        "server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)\n"
        "server.bind(('127.0.0.1', 8080))\n"
        "server.listen(5)\n"
        "print('[*] Server listening on 127.0.0.1:8080')\n\n"
        "while True:\n"
        "    client, addr = server.accept()\n"
        "    print(f'[+] Connection established with {addr}')\n"
        "    client.send(b'Hello from Strawberry Socket Server!\\n')\n"
        "    client.close()\n"
    ),
    "tcp_client.py": (
        "import socket\n\n"
        "client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)\n"
        "client.connect(('127.0.0.1', 8080))\n"
        "data = client.recv(1024)\n"
        "print('Received from server:', data.decode())\n"
        "client.close()\n"
    ),
    "schema_ddl.sql": (
        "-- Database Management Systems Lab - Experiment 1\n"
        "CREATE TABLE Students (\n"
        "    id INT PRIMARY KEY,\n"
        "    name VARCHAR(100) NOT NULL,\n"
        "    department VARCHAR(50) DEFAULT 'CSE',\n"
        "    cgpa DECIMAL(3, 2)\n"
        ");\n\n"
        "INSERT INTO Students VALUES (1, 'Alice Smith', 'CSE', 9.2);\n"
        "INSERT INTO Students VALUES (2, 'Bob Jones', 'CSE', 8.7);\n"
        "SELECT * FROM Students WHERE cgpa > 9.0;\n"
    ),
    "threads.java": (
        "public class ThreadDemo extends Thread {\n"
        "    public void run() {\n"
        "        for (int i = 1; i <= 5; i++) {\n"
        "            System.out.println(Thread.currentThread().getName() + ' count: ' + i);\n"
        "            try { Thread.sleep(500); } catch (Exception e) {}\n"
        "        }\n"
        "    }\n"
        "    public static void main(String[] args) {\n"
        "        ThreadDemo t1 = new ThreadDemo();\n"
        "        ThreadDemo t2 = new ThreadDemo();\n"
        "        t1.start();\n"
        "        t2.start();\n"
        "    }\n"
        "}\n"
    ),
    "round_robin.c": (
        "#include <stdio.h>\n\n"
        "int main() {\n"
        "    int n = 3, time_quantum = 2;\n"
        "    int burst[] = {6, 4, 2};\n"
        "    int rem_burst[] = {6, 4, 2};\n"
        "    int t = 0, done = 0;\n"
        "    printf(\"Round Robin Scheduling (Quantum = %d)\\n\", time_quantum);\n"
        "    while (!done) {\n"
        "        done = 1;\n"
        "        for (int i = 0; i < n; i++) {\n"
        "            if (rem_burst[i] > 0) {\n"
        "                done = 0;\n"
        "                if (rem_burst[i] > time_quantum) {\n"
        "                    t += time_quantum;\n"
        "                    rem_burst[i] -= time_quantum;\n"
        "                } else {\n"
        "                    t += rem_burst[i];\n"
        "                    rem_burst[i] = 0;\n"
        "                    printf(\"Process %d finished at time %d\\n\", i + 1, t);\n"
        "                }\n"
        "            }\n"
        "        }\n"
        "    }\n"
        "    return 0;\n"
        "}\n"
    ),
}

def get_demo_hash(filename: str) -> str:
    content = DEMO_PROGRAMS.get(filename, "").encode("utf-8")
    return hashlib.sha256(content).hexdigest()

SEED_YEARS = [
    {"id": "year-2", "year_number": 2, "display_name": "2nd Year"},
    {"id": "year-3", "year_number": 3, "display_name": "3rd Year"},
    {"id": "year-4", "year_number": 4, "display_name": "4th Year"},
]

SEED_SEMESTERS = [
    {"id": "sem-3", "year_id": "year-2", "semester_number": 3, "display_name": "Semester 3"},
    {"id": "sem-4", "year_id": "year-2", "semester_number": 4, "display_name": "Semester 4"},
    {"id": "sem-5", "year_id": "year-3", "semester_number": 5, "display_name": "Semester 5"},
    {"id": "sem-6", "year_id": "year-3", "semester_number": 6, "display_name": "Semester 6"},
    {"id": "sem-7", "year_id": "year-4", "semester_number": 7, "display_name": "Semester 7"},
    {"id": "sem-8", "year_id": "year-4", "semester_number": 8, "display_name": "Semester 8"},
]

SEED_SUBJECTS = [
    {"id": "sub-cn", "semester_id": "sem-3", "subject_code": "CS301", "subject_name": "Computer Networks"},
    {"id": "sub-dbms", "semester_id": "sem-3", "subject_code": "CS302", "subject_name": "Database Management Systems"},
    {"id": "sub-java", "semester_id": "sem-3", "subject_code": "CS303", "subject_name": "Java Programming"},
    {"id": "sub-os", "semester_id": "sem-4", "subject_code": "CS401", "subject_name": "Operating Systems"},
]

SEED_EXPERIMENTS = [
    {
        "id": "exp-cn-1",
        "subject_id": "sub-cn",
        "experiment_number": 1,
        "title": "Socket Programming",
        "description": "TCP client-server socket communication",
        "filename": "socket_server.py",
    },
    {
        "id": "exp-cn-2",
        "subject_id": "sub-cn",
        "experiment_number": 2,
        "title": "TCP Client Server",
        "description": "Connecting TCP client to echo server",
        "filename": "tcp_client.py",
    },
    {
        "id": "exp-dbms-1",
        "subject_id": "sub-dbms",
        "experiment_number": 1,
        "title": "DDL and DML Commands",
        "description": "Table creation, insertion and queries",
        "filename": "schema_ddl.sql",
    },
    {
        "id": "exp-java-1",
        "subject_id": "sub-java",
        "experiment_number": 1,
        "title": "Multithreading",
        "description": "Concurrent thread execution in Java",
        "filename": "threads.java",
    },
    {
        "id": "exp-os-1",
        "subject_id": "sub-os",
        "experiment_number": 1,
        "title": "CPU Scheduling Algorithm",
        "description": "Round Robin CPU scheduling implementation in C",
        "filename": "round_robin.c",
    },
]
