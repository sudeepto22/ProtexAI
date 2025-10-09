import logging
import time
from types import TracebackType
import paho.mqtt.client as mqtt
from typing import Optional, Callable, Type
from common.config.mqtt_config import MQTTConfig


class MQTTClient:
    """
    Context manager for MQTT client
    """
    
    def __init__(
        self,
        client_id: str,
        logger: logging.Logger,
        on_message: Optional[Callable] = None,
        background_loop: bool = False
    ) -> None:
        """
        Arguments:
            client_id: Client identifier
            logger: Logger instance
            on_message: Optional callback for message reception (for consumers)
            background_loop: If True, start loop_start(), otherwise use manual loop
        
        Returns:
            None
        """
        self.client_id = client_id
        self.logger = logger
        self.on_message = on_message
        self.background_loop = background_loop
        self.client = None
        self.config = MQTTConfig()
    
    def __enter__(self) -> mqtt.Client:
        """
        Create client and connect to broker
        
        Returns:
            Connected MQTT client
        """
        self.client = mqtt.Client(
            client_id=self.client_id,
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2
        )
        
        if self.on_message:
            self.client.on_message = self.on_message
        
        try:
            self.logger.info(f'Connecting to MQTT broker at {self.config.BROKER_HOST}:{self.config.BROKER_PORT}')
            self.client.connect(
                self.config.BROKER_HOST,
                self.config.BROKER_PORT,
                keepalive=self.config.KEEPALIVE
            )
            
            # Start background loop if requested (needed for connection to complete)
            if self.background_loop:
                self.client.loop_start()
                time.sleep(2)  # Give loop time to establish connection
                self.logger.info('Background network loop started')
            
            self.logger.info('Connected to MQTT broker')
            
            return self.client
            
        except Exception as e:
            self.logger.error(f'Failed to connect: {e}')
            raise
    
    def __exit__(self, exc_type: Type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None) -> None:
        """
        Exit context: disconnect and cleanup
        """
        if self.client:
            try:
                # Stop network loop if it was started
                if self.background_loop:
                    try:
                        self.client.loop_stop()
                        self.logger.info('Network loop stopped')
                    except:
                        pass
                
                self.client.disconnect()
                self.logger.info('Disconnected from MQTT broker')
                
            except Exception as e:
                self.logger.error(f'Error during disconnect: {e}')
        return None