#!/bin/bash

# InventAI Quick Start Script
# Usage: bash quick-start.sh [command]

set -e

BLUE='\033[0;34m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 InventAI Backend Services - Quick Start${NC}"
echo ""

# Functions
start_services() {
    echo -e "${YELLOW}Starting all services...${NC}"
    docker-compose up -d
    echo -e "${GREEN}✓ All services started${NC}"
    sleep 5
    check_health
}

stop_services() {
    echo -e "${YELLOW}Stopping all services...${NC}"
    docker-compose stop
    echo -e "${GREEN}✓ All services stopped${NC}"
}

restart_services() {
    echo -e "${YELLOW}Restarting all services...${NC}"
    docker-compose restart
    echo -e "${GREEN}✓ All services restarted${NC}"
    sleep 5
    check_health
}

check_health() {
    echo -e "${BLUE}📊 Checking service health...${NC}"
    echo ""
    
    services=(
        "auth-service:8001"
        "business-service:8002"
        "patent-service:8003"
        "research-service:8004"
        "cad-service:8005"
        "physics-service:8006"
        "report-service:8008"
    )
    
    for service in "${services[@]}"; do
        IFS=':' read -r name port <<< "$service"
        if curl -s http://localhost:$port/health > /dev/null 2>&1; then
            echo -e "${GREEN}✓${NC} $name (Port $port)"
        else
            echo -e "${RED}✗${NC} $name (Port $port) - Not responding"
        fi
    done
    
    echo ""
    echo -e "${BLUE}📊 Infrastructure Status:${NC}"
    docker-compose ps --services | while read service; do
        if docker-compose ps $service | grep -q "Up"; then
            echo -e "${GREEN}✓${NC} $service"
        else
            echo -e "${RED}✗${NC} $service"
        fi
    done
}

view_logs() {
    service=${1:-all}
    if [ "$service" = "all" ]; then
        echo -e "${YELLOW}Viewing logs for all services (Ctrl+C to exit)...${NC}"
        docker-compose logs -f
    else
        echo -e "${YELLOW}Viewing logs for $service (Ctrl+C to exit)...${NC}"
        docker-compose logs -f $service
    fi
}

enter_service() {
    service=$1
    if [ -z "$service" ]; then
        echo -e "${RED}Usage: $0 shell <service-name>${NC}"
        echo "Available services:"
        docker-compose config --services
        exit 1
    fi
    echo -e "${YELLOW}Entering $service container...${NC}"
    docker-compose exec $service bash
}

clean() {
    echo -e "${YELLOW}🧹 Cleaning up...${NC}"
    docker-compose down -v
    echo -e "${GREEN}✓ Cleaned up${NC}"
}

rebuild() {
    service=${1:-all}
    echo -e "${YELLOW}Rebuilding $service...${NC}"
    if [ "$service" = "all" ]; then
        docker-compose up -d --build
    else
        docker-compose up -d --build $service
    fi
    echo -e "${GREEN}✓ Rebuild complete${NC}"
}

show_urls() {
    echo -e "${BLUE}📋 Service URLs:${NC}"
    echo ""
    echo -e "${GREEN}Frontend:${NC}"
    echo "  Web UI: http://localhost:3001"
    echo "  API Gateway: http://localhost:8080"
    echo ""
    echo -e "${GREEN}Microservices:${NC}"
    echo "  Auth Service: http://localhost:8001"
    echo "  Business Service: http://localhost:8002"
    echo "  Patent Service: http://localhost:8003"
    echo "  Research Service: http://localhost:8004"
    echo "  CAD Service: http://localhost:8005"
    echo "  Physics Service: http://localhost:8006"
    echo ""
    echo -e "${GREEN}Infrastructure:${NC}"
    echo "  PostgreSQL: localhost:5432"
    echo "  Neo4j Browser: http://localhost:7474"
    echo "  Redis: localhost:6379"
    echo "  RabbitMQ: http://localhost:15672"
    echo "  MinIO Console: http://localhost:9001"
    echo "  ChromaDB: http://localhost:8000"
    echo "  Prometheus: http://localhost:9090"
    echo "  Grafana: http://localhost:3000"
    echo "  Jaeger: http://localhost:16686"
}

show_help() {
    echo -e "${BLUE}Usage: $0 [command]${NC}"
    echo ""
    echo -e "${YELLOW}Commands:${NC}"
    echo "  start              Start all services"
    echo "  stop               Stop all services"
    echo "  restart            Restart all services"
    echo "  health             Check health of all services"
    echo "  logs [service]     View logs (default: all)"
    echo "  shell <service>    Enter service container"
    echo "  rebuild [service]  Rebuild services (default: all)"
    echo "  clean              Stop all services and remove volumes"
    echo "  urls               Show all service URLs"
    echo "  help               Show this help message"
    echo ""
    echo -e "${YELLOW}Examples:${NC}"
    echo "  $0 start"
    echo "  $0 logs auth-service"
    echo "  $0 shell cad-service"
    echo "  $0 rebuild innovation-engine"
}

# Main
case "${1:-help}" in
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    restart)
        restart_services
        ;;
    health)
        check_health
        ;;
    logs)
        view_logs ${2:-all}
        ;;
    shell)
        enter_service $2
        ;;
    rebuild)
        rebuild ${2:-all}
        ;;
    clean)
        clean
        ;;
    urls)
        show_urls
        ;;
    help)
        show_help
        ;;
    *)
        echo -e "${RED}Unknown command: $1${NC}"
        show_help
        exit 1
        ;;
esac
