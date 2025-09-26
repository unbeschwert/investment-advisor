#!/bin/bash
# Comprehensive PDF Renaming Script for Investment Advisor Stocks Data
# This script renames all PDF files from ugly ISIN-based names to beautiful company names
# with language indicators (_EN for English, _DE for German)

# Configuration
CSV_FILE="data/2025-09-23_data_EN.csv"
PDF_DIR="data/2025-09-23"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to clean filename (replace problematic characters)
clean_filename() {
    echo "$1" | sed 's/[\/\\:*?"<>|]/_/g' | sed "s/'/_/g"
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    if [[ ! -f "$CSV_FILE" ]]; then
        print_error "CSV file $CSV_FILE not found!"
        print_error "Please make sure you're running this script from the repository root directory."
        exit 1
    fi
    
    if [[ ! -d "$PDF_DIR" ]]; then
        print_error "PDF directory $PDF_DIR not found!"
        print_error "Please make sure you're running this script from the repository root directory."
        exit 1
    fi
    
    print_success "Prerequisites check passed!"
}

# Main renaming function
rename_pdfs() {
    print_status "Starting PDF renaming process..."
    print_status "CSV file: $CSV_FILE"
    print_status "PDF directory: $PDF_DIR"
    echo ""
    
    # Counters for statistics
    renamed_count=0
    already_exists_count=0
    not_found_count=0
    
    # Read CSV file (skip header line)
    tail -n +2 "$CSV_FILE" | while IFS=';' read -r isin ticker name sector industry market date currency price global_eval market_cap target_price ytd_performance sensitivity earnings_revision valuation_rating technical_trend four_weeks_performance reference_index long_term_pe long_term_growth return_on_equity ebit equity_on_assets book_value_price stars industry_global_eval total_revenue net_income net_income_2 current_ratio long_term_debt revenues_on_assets cash_flow_on_revenues expected_dividend; do
        
        # Remove any leading/trailing whitespace
        isin=$(echo "$isin" | xargs)
        name=$(echo "$name" | xargs)
        
        # Skip empty lines
        if [[ -z "$isin" || -z "$name" ]]; then
            continue
        fi
        
        # Create clean filename
        clean_name=$(clean_filename "$name")
        
        # Check for English version (-en suffix)
        en_file=$(find "$PDF_DIR" -name "${isin}-*-en.pdf" 2>/dev/null | head -1)
        if [[ -f "$en_file" ]]; then
            newname="${PDF_DIR}/${clean_name}_EN.pdf"
            if [[ ! -f "$newname" ]]; then
                print_success "Renaming EN: $(basename "$en_file") -> $(basename "$newname")"
                mv "$en_file" "$newname"
                ((renamed_count++))
            else
                print_warning "Already exists: $(basename "$newname")"
                ((already_exists_count++))
            fi
        fi
        
        # Check for German version (-de suffix)
        de_file=$(find "$PDF_DIR" -name "${isin}-*-de.pdf" 2>/dev/null | head -1)
        if [[ -f "$de_file" ]]; then
            newname="${PDF_DIR}/${clean_name}_DE.pdf"
            if [[ ! -f "$newname" ]]; then
                print_success "Renaming DE: $(basename "$de_file") -> $(basename "$newname")"
                mv "$de_file" "$newname"
                ((renamed_count++))
            else
                print_warning "Already exists: $(basename "$newname")"
                ((already_exists_count++))
            fi
        fi
        
        # Check for files without language suffix (exact ISIN match)
        exact_file=$(find "$PDF_DIR" -name "${isin}.pdf" 2>/dev/null | head -1)
        if [[ -f "$exact_file" ]]; then
            newname="${PDF_DIR}/${clean_name}.pdf"
            if [[ ! -f "$newname" ]]; then
                print_success "Renaming: $(basename "$exact_file") -> $(basename "$newname")"
                mv "$exact_file" "$newname"
                ((renamed_count++))
            else
                print_warning "Already exists: $(basename "$newname")"
                ((already_exists_count++))
            fi
        fi
        
        # Check for files with ISIN prefix (no language suffix)
        prefix_file=$(find "$PDF_DIR" -name "${isin}-*.pdf" 2>/dev/null | grep -v -- "-en.pdf\|-de.pdf" | head -1)
        if [[ -f "$prefix_file" ]]; then
            newname="${PDF_DIR}/${clean_name}.pdf"
            if [[ ! -f "$newname" ]]; then
                print_success "Renaming: $(basename "$prefix_file") -> $(basename "$newname")"
                mv "$prefix_file" "$newname"
                ((renamed_count++))
            else
                print_warning "Already exists: $(basename "$newname")"
                ((already_exists_count++))
            fi
        fi
    done
    
    echo ""
    print_status "Renaming completed!"
    print_success "Files renamed: $renamed_count"
    print_warning "Files already existed: $already_exists_count"
    print_error "Files not found: $not_found_count"
}

# Function to show final statistics
show_statistics() {
    echo ""
    print_status "=== Final Statistics ==="
    
    total_files=$(ls "$PDF_DIR"/*.pdf 2>/dev/null | wc -l)
    clean_files=$(ls "$PDF_DIR"/*.pdf 2>/dev/null | grep -v "_EN\|_DE" | wc -l)
    en_files=$(ls "$PDF_DIR"/*_EN.pdf 2>/dev/null | wc -l)
    de_files=$(ls "$PDF_DIR"/*_DE.pdf 2>/dev/null | wc -l)
    ugly_files=$(ls "$PDF_DIR"/*-EUR-*.pdf 2>/dev/null | wc -l)
    
    echo "Total PDF files: $total_files"
    echo "Clean named files (no language suffix): $clean_files"
    echo "English versions (_EN): $en_files"
    echo "German versions (_DE): $de_files"
    echo "Files with ugly names remaining: $ugly_files"
    
    if [[ $ugly_files -gt 0 ]]; then
        echo ""
        print_warning "Remaining ugly-named files:"
        ls "$PDF_DIR"/*-EUR-*.pdf 2>/dev/null | head -5
        if [[ $ugly_files -gt 5 ]]; then
            echo "... and $((ugly_files - 5)) more"
        fi
    fi
}

# Main execution
main() {
    echo "=========================================="
    echo "PDF Renaming Script for Investment Advisor"
    echo "=========================================="
    echo ""
    
    check_prerequisites
    rename_pdfs
    show_statistics
    
    echo ""
    print_success "Script completed successfully!"
    print_status "Your PDF files now have clean, readable names with language indicators."
}

# Run the script
main "$@"
