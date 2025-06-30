FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    openssh-server \
    mpich libmpich-dev libmpich12 \
    sudo && \
    rm -rf /var/lib/apt/lists/*

ENV LD_LIBRARY_PATH=/lib/x86_64-linux-gnu

ENV PYTHONUNBUFFERED=1

RUN useradd -m mpiuser && echo "mpiuser:mpiuser" | chpasswd && adduser mpiuser sudo

RUN mkdir -p /var/run/sshd /home/mpiuser/.ssh

# Copiar claves ssh y configurar permisos
COPY ssh/ /home/mpiuser/.ssh/

RUN chown -R mpiuser:mpiuser /home/mpiuser/.ssh && \
    chmod 700 /home/mpiuser/.ssh && \
    chmod 600 /home/mpiuser/.ssh/mpi_cluster_key && \
    chmod 644 /home/mpiuser/.ssh/mpi_cluster_key.pub && \
    chmod 644 /home/mpiuser/.ssh/authorized_keys && \
    chmod 644 /home/mpiuser/.ssh/config

RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config && \
    echo "PermitUserEnvironment yes" >> /etc/ssh/sshd_config

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY nodo.py .

RUN ln -s /lib/x86_64-linux-gnu/libmpich.so.12 /usr/lib/libmpi.so.12

USER mpiuser

CMD ["/usr/sbin/sshd", "-D"]