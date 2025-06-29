FROM python:3.11-slim

# Instalar dependencias necesarias
RUN apt-get update && apt-get install -y \
    openssh-server \
    mpich libmpich-dev \
    sudo && \
    rm -rf /var/lib/apt/lists/*

# Crear usuario
RUN useradd -m mpiuser && echo "mpiuser:mpiuser" | chpasswd && adduser mpiuser sudo

# Crear directorios necesarios
RUN mkdir -p /var/run/sshd && mkdir -p /home/mpiuser/.ssh

# Configurar SSH para permitir login
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config && \
    echo "PermitUserEnvironment yes" >> /etc/ssh/sshd_config

# Agregar configuración SSH para evitar errores con claves
RUN echo -e "Host *\n\tStrictHostKeyChecking no\n\tUserKnownHostsFile=/dev/null" > /home/mpiuser/.ssh/config

# Dar permisos correctos
RUN chown -R mpiuser:mpiuser /home/mpiuser/.ssh && \
    chmod 700 /home/mpiuser/.ssh && \
    chmod 600 /home/mpiuser/.ssh/id_rsa || true && \
    chmod 644 /home/mpiuser/.ssh/authorized_keys || true && \
    chmod 644 /home/mpiuser/.ssh/config

# Instalar dependencias de Python
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar scripts
COPY . .

# Copiar entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

USER root
ENTRYPOINT ["/entrypoint.sh"]
