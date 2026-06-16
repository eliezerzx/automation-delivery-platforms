"""
Logger que envia mensagens em tempo real para o painel Tkinter.
Permite capturar logs enquanto a automação está rodando.
"""

import logging
import queue
from typing import Optional, Callable


class TkinterQueueHandler(logging.Handler):
    """Handler de logging que envia mensagens para uma fila (queue)."""
    
    def __init__(self, log_queue: queue.Queue):
        super().__init__()
        self.log_queue = log_queue
    
    def emit(self, record):
        """Envia mensagem de log para a fila."""
        try:
            msg = self.format(record)
            self.log_queue.put({
                'mensagem': msg,
                'nivel': record.levelname.lower()
            })
        except Exception:
            self.handleError(record)


class LoggerTkinter:
    """Gerenciador de logging para Tkinter com suporte a tempo real."""
    
    def __init__(self, callback: Optional[Callable] = None):
        """
        Inicializa o logger.
        
        Args:
            callback: Função para receber logs em tempo real
        """
        self.queue = queue.Queue()
        self.callback = callback
        self.logger = logging.getLogger('automacao')
        self.logger.setLevel(logging.DEBUG)
        
        # Handler para fila (tempo real)
        queue_handler = TkinterQueueHandler(self.queue)
        queue_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        ))
        self.logger.addHandler(queue_handler)
    
    def obter_logs(self):
        """Obtém todos os logs pendentes da fila."""
        logs = []
        try:
            while True:
                log = self.queue.get_nowait()
                logs.append(log)
        except queue.Empty:
            pass
        return logs
    
    def info(self, msg):
        self.logger.info(msg)
    
    def error(self, msg):
        self.logger.error(msg)
    
    def warning(self, msg):
        self.logger.warning(msg)
    
    def success(self, msg):
        """Log de sucesso (verde)."""
        self.logger.info(f"✓ {msg}")


# Instância global
_logger_instance = None


def obter_logger(callback=None):
    """Retorna instância global do logger."""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = LoggerTkinter(callback)
    return _logger_instance
