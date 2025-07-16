#!/bin/bash

# Warna untuk output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

show_help() {
    echo "Setup script untuk Bejo Backend"
    echo ""
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  build           Build dan start services"
    echo "  pull-models     Pull model AI saja"
    echo "  start           Start services yang sudah ada"
    echo "  stop            Stop semua services"
    echo "  clean           Hapus semua containers dan volumes"
    echo "  check-models    Cek status model"
    echo ""
    echo "Options:"
    echo "  --with-model    Download model AI saat build"
    echo "  --help, -h      Show help"
    echo ""
    echo "Examples:"
    echo "  $0 build                # Build tanpa download model"
    echo "  $0 build --with-model   # Build dengan download model"
    echo "  $0 pull-models          # Download model saja"
    echo ""
    echo "Note: Download model membutuhkan waktu 10-20 menit"
}

check_models() {
    print_info "Checking model status..."
    
    if ! docker-compose ps ollama | grep -q "Up"; then
        print_error "Ollama service tidak running. Jalankan '$0 start' dulu."
        return 1
    fi
    
    models=$(docker-compose exec ollama ollama list 2>/dev/null)
    if echo "$models" | grep -q "qwen2.5:3b " && echo "$models" | grep -q "nomic-embed-text"; then
        print_success "Semua model tersedia!"
        echo "$models"
    else
        print_warning "Model belum lengkap. Jalankan '$0 pull-models'."
        echo "$models"
    fi
}

pull_models() {
    print_info "Memulai proses download model AI..."
    print_warning "⏳ Proses ini bisa memakan waktu 10-20 menit tergantung koneksi internet"
    
    # Start ollama service saja
    docker-compose up -d ollama
    
    # Tunggu ollama ready dengan timeout lebih lama
    print_info "Menunggu Ollama service ready..."
    local attempts=0
    local max_attempts=40
    
    while ! docker-compose exec ollama ollama list > /dev/null 2>&1; do
        attempts=$((attempts + 1))
        if [ $attempts -ge $max_attempts ]; then
            print_error "Ollama service tidak ready setelah 2 menit. Coba restart."
            exit 1
        fi
        echo "😴 Ollama warming up... ($attempts/$max_attempts)"
        sleep 3
    done
    
    print_success "Ollama service ready!"
    
    # Pull models dengan progress indicator
    print_info "📦 Mengunduh model qwen2.5:3b ..."
    print_info "☕ Ambil kopi dulu, ini bakal lama..."
    docker-compose exec ollama ollama pull qwen2.5:3b 
    
    print_info "🧠 Mengunduh model nomic-embed-text (±274MB)..."
    docker-compose exec ollama ollama pull nomic-embed-text
    
    print_success "Semua model berhasil didownload!"
    print_info "Restart backend service untuk apply model..."
    docker-compose restart bejo-backend
}

build_services() {
    local with_model=false
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --with-model)
                with_model=true
                shift
                ;;
            *)
                shift
                ;;
        esac
    done
    
    print_info "Building services..."
    
    # Build dan start services
    docker-compose up -d --build
    
    if [ "$with_model" = true ]; then
        print_info "Flag --with-model detected, akan download model..."
        pull_models
        print_info "Restart backend service untuk apply model..."
        docker-compose restart bejo-backend
    else
        print_warning "Model tidak didownload. Jalankan '$0 pull-models' untuk download model."
    fi
    
    print_success "Services berhasil dibangun dan dijalankan!"
    print_info "Backend available di: http://localhost:8000"
    print_info "Qdrant available di: http://localhost:6333"
}

start_services() {
    print_info "Starting services..."
    docker-compose up -d
    print_success "Services started!"
}

stop_services() {
    print_info "Stopping services..."
    docker-compose down
    print_success "Services stopped!"
}

clean_services() {
    print_warning "Ini akan menghapus semua containers, images, dan volumes!"
    read -p "Apakah Anda yakin? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Cleaning up..."
        docker-compose down -v --rmi all
        docker system prune -f
        print_success "Cleanup complete!"
    else
        print_info "Cleanup dibatalkan."
    fi
}

# Main script
case "$1" in
    build)
        shift
        build_services "$@"
        ;;
    pull-models)
        pull_models
        ;;
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    clean)
        clean_services
        ;;
    check-models)
        check_models
        ;;
    --help|-h|help)
        show_help
        ;;
    *)
        print_error "Command tidak dikenali: $1"
        echo ""
        show_help
        exit 1
        ;;
esac