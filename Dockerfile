FROM python:3.9-slim

# --- 1. Install dependencies ---
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-tk \
    mpich libmpich-dev \
    openssh-server \
    sudo \
    xauth \
    && rm -rf /var/lib/apt/lists/*

# --- 2. Create MPI symlinks ---
RUN ln -s /usr/lib/x86_64-linux-gnu/libmpich.so.12 /usr/lib/libmpi.so.12 && \
    ln -s /usr/lib/x86_64-linux-gnu/libmpich.so.12 /usr/lib/x86_64-linux-gnu/libmpi.so.12

# --- 3. Create user and setup ---
RUN useradd -m mpiuser && \
    echo "mpiuser:mpiuser" | chpasswd && \
    adduser mpiuser sudo

# --- 4. SSH setup ---
RUN mkdir -p /var/run/sshd /home/mpiuser/.ssh && \
    chmod 700 /home/mpiuser/.ssh

COPY ssh/id_rsa /home/mpiuser/.ssh/id_rsa
COPY ssh/id_rsa.pub /home/mpiuser/.ssh/authorized_keys

RUN chmod 600 /home/mpiuser/.ssh/id_rsa /home/mpiuser/.ssh/authorized_keys && \
    chown -R mpiuser:mpiuser /home/mpiuser/.ssh

# Configure SSH (as root)
RUN sed -i \
    -e 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' \
    -e 's/#PasswordAuthentication yes/PasswordAuthentication yes/' \
    /etc/ssh/sshd_config && \
    echo "PermitUserEnvironment yes" >> /etc/ssh/sshd_config && \
    echo "StrictHostKeyChecking no" >> /etc/ssh/ssh_config

# --- 5. Environment setup ---
ENV PYTHONUNBUFFERED=1
ENV LD_LIBRARY_PATH=/lib/x86_64-linux-gnu
ENV PYTHONPATH=/app
ENV DISPLAY=host.docker.internal:0.0

# --- 6. Python setup ---
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY controlador_nodos.py .
COPY Nodos ./Nodos
COPY modelos ./modelos
COPY images ./images

# --- 7. Final setup ---
EXPOSE 22
USER mpiuser

# --- 8. Start SSH ---
CMD ["/usr/sbin/sshd", "-D"]