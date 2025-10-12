#!/bin/bash

# ChatBot AI - Frontend Setup Script
# Run this script to set up the frontend

echo "🚀 ChatBot AI - Frontend Setup"
echo "================================"
echo ""

# Navigate to AIR directory
cd /home/gbemi/AIR

# Ask user which method they prefer
echo "Choose your setup method:"
echo "1) Create React App (Recommended - More stable)"
echo "2) Vite (Faster, but requires Node 20+)"
read -p "Enter choice (1 or 2): " choice

if [ "$choice" == "1" ]; then
    echo ""
    echo "📦 Setting up with Create React App..."
    npx create-react-app frontend
    
    cd frontend
    
    echo ""
    echo "📦 Installing additional dependencies..."
    npm install axios lucide-react
    npm install -D tailwindcss postcss autoprefixer
    
    echo ""
    echo "🎨 Initializing Tailwind CSS..."
    npx tailwindcss init -p
    
    echo ""
    echo "✅ Frontend structure created!"
    echo ""
    echo "📝 Next steps:"
    echo "1. I'll help you add the component files"
    echo "2. Configure Tailwind CSS"
    echo "3. Start the development server"
    
elif [ "$choice" == "2" ]; then
    echo ""
    echo "📦 Setting up with Vite..."
    npm create vite@latest frontend -- --template react
    
    cd frontend
    
    echo ""
    echo "📦 Installing dependencies..."
    npm install
    npm install axios lucide-react
    npm install -D tailwindcss postcss autoprefixer
    
    echo ""
    echo "🎨 Initializing Tailwind CSS..."
    npx tailwindcss init -p
    
    echo ""
    echo "✅ Frontend structure created!"
    echo ""
    echo "📝 Next steps:"
    echo "1. I'll help you add the component files"
    echo "2. Configure Tailwind CSS"
    echo "3. Start the development server"
    
else
    echo "❌ Invalid choice. Please run the script again and choose 1 or 2."
    exit 1
fi

echo ""
echo "🎉 Setup complete! Let the AI assistant know you're ready for the next step."
