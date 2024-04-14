
### Currency Platform

#### Overview



It's built using Django and Docker for easy setup and deployment.

#### Getting Started

##### Prerequisites

- Docker
- Docker Compose

#### Quick Start

To get the platform up and running, follow these steps:

1. Start the services using Docker Compose:
    ```bash
    docker-compose up -d
    ```
2. Check if the services are running:
    ```bash
    docker ps
    ```

3. Monitor the logs of the currency platform:
    ```bash
    docker logs -f currency_platform
    ```

4. Access the platform's bash interface:
    ```bash
    docker exec -it currency_platform bash
    ```

5. Inside the Docker container, you can execute various management commands:
    - Run tests:
        ```bash
        python manage.py test currency_exchange.tests
        ```
    - Create a superuser:
        ```bash
        python manage.py createsuperuser
        ```

#### Improvements and Decisions

- **Requirements Management**: Use `pip compile` or similar to generate `requirements.txt`.
- **Settings Modularization**: Separate Django settings into different files (e.g., drf.py, etc.) for better organization and readability.
- **Code Reusability**: Add mixin at the RestView level to improve the reuse of cache data code.
- **Performance Enhancement**: Explore the use of Django cache or Redis to improve response times.
- **API Documentation**: Consider making Open API documentation public.

### Challenges and Improvement Areas
Despite progress made, several areas require attention and enhancement:

1) Celery Integration: The Celery setup, along with RabbitMQ as a broker and Flower for monitoring, remains pending due to time constraints.

2) Data Loading Optimization: Implement (Celery + RabbitMQ) with django-celery-beat for efficient daily data loading. Additionally, consider defining tasks to prevent blocking REST calls during data operations.

3) Adapter Code Flexibility: The current plug-and-play approach of the Provider.adapter_code introduces complexity and testing challenges. Exploring alternative, more robust solutions could enhance reliability and maintainability.

4) Incomplete Implementation: While significant functionality has been developed, not all aspects of the project are fully implemented. Continuous efforts are required to fill the gaps and ensure comprehensive coverage within the project timeline.

5) Real-time Graph Views: The intention to utilize the chartjs library for real-time data visualization via AJAX calls remains unaddressed. Implementing this feature could significantly enhance user experience and data presentation capabilities.