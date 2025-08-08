# 🚚 AI Shipping Agent with FedEx Integration

A powerful, AI-driven shipping assistant that provides real-time FedEx quotes through both conversational AI and direct form input. Built with Streamlit, LangChain, and live FedEx API integration.

![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white)
![FedEx](https://img.shields.io/badge/FedEx-4D148C?style=for-the-badge&logo=fedex&logoColor=white)

## ✨ Features

### 🤖 **AI-Powered Chat Interface**
- **Natural Language Processing**: Ask shipping questions in plain English
- **Real-time FedEx API Calls**: AI agent calls live FedEx APIs using LangChain tools
- **Conversation Memory**: Maintains context across multiple questions
- **Debug Information**: See exactly which tools the AI called and their responses

### 📦 **Direct Form Integration**
- **Quick Quote Form**: Get FedEx rates without AI interaction
- **Address Validation**: Complete street-level address support
- **Package Details**: Weight and dimension inputs with validation
- **Instant Results**: Direct API calls for immediate quotes

### 🔧 **Advanced Functionality**
- **Copy to Clipboard**: One-click copy of package details from AI responses
- **Service Comparison**: Side-by-side comparison of FedEx Ground, Express Saver, and 2Day
- **Error Handling**: Robust error handling with user-friendly messages
- **Responsive Design**: Works on desktop, tablet, and mobile devices

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- OpenAI API key
- FedEx Developer Account (for API credentials)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/kikobarr/AI_Shipping_Agent.git
   cd AI_Shipping_Agent
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the project root:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   FEDEX_API_KEY=your_fedex_api_key
   FEDEX_SECRET_KEY=your_fedex_secret_key
   FEDEX_ACCOUNT_NUMBER=your_fedex_account_number
   FEDEX_METER_NUMBER=your_fedex_meter_number
   ```

5. **Run the application**
   ```bash
   streamlit run AI_Agent.py
   ```

## 🎯 Usage Examples

### 💬 **Chat with AI Agent**
```
User: "Get shipping quotes for a 5lb package from New York to Los Angeles"
AI: I'll help you get FedEx shipping quotes. Let me gather that information...

[AI calls FedEx API and returns:]
- FedEx Ground: $18.38 (4 business days)
- FedEx Express Saver: $32.54 (3 business days)  
- FedEx 2Day: $37.26 (2 business days)
```

### 📝 **Direct Form Input**
1. Fill out origin and destination addresses
2. Enter package weight and dimensions
3. Click "Get FedEx Shipping Quotes"
4. View instant results with pricing and transit times

## 🏗️ Architecture

### **Core Components**

```
AI_Agent.py                 # Main Streamlit application
├── Chat Interface          # AI conversation with tool calling
├── Direct Form            # Manual quote input form
└── Results Display        # Unified quote presentation

services/
├── langchain_agent.py     # AI agent with LangChain integration
├── fedex_tool.py         # FedEx API tools for AI agent
├── fedexAPI.py           # Core FedEx API wrapper
└── shipping_integration.py # Direct form API integration
```

### **Data Flow**

1. **AI Path**: User → Chat → LangChain Agent → FedEx Tools → FedEx API → Results
2. **Direct Path**: User → Form → Shipping Integration → FedEx API → Results

## 🔧 Configuration

### **FedEx API Setup**
1. Register at [FedEx Developer Portal](https://developer.fedex.com/)
2. Create a new application
3. Get your API credentials:
   - API Key
   - Secret Key
   - Account Number
   - Meter Number

### **OpenAI Setup**
1. Get API key from [OpenAI Platform](https://platform.openai.com/)
2. Add to environment variables
3. Ensure sufficient credits for API calls

### **Supported FedEx Services**
- **FedEx Ground**: Most economical, 4 business days
- **FedEx Express Saver**: 3 business days
- **FedEx 2Day**: 2 business days

## 🎨 Features in Detail

### **AI Agent Capabilities**
- **Tool Calling**: Uses LangChain to call FedEx APIs based on natural language
- **Context Awareness**: Remembers previous questions in conversation
- **Error Recovery**: Handles API errors gracefully with helpful messages
- **Debug Mode**: Shows tool calls and API responses for transparency

### **User Experience**
- **Single Page Design**: Everything in one clean interface
- **Copy Functionality**: Easy copying of package details
- **Responsive Layout**: Adapts to different screen sizes
- **Accessibility**: High contrast mode and keyboard navigation

### **API Integration**
- **Live FedEx Sandbox**: Real API calls to FedEx testing environment
- **Rate Shopping**: Compares multiple service levels
- **Address Validation**: Ensures accurate shipping calculations
- **Error Handling**: Comprehensive error messages and recovery

## 🧪 Testing

### **Run Tests**
```bash
# Test FedEx API integration
python test_fedex_integration.py

# Test AI vs Direct comparison
python test_ai_vs_direct.py
```

### **Sample Test Cases**
- **Domestic Shipping**: California to New York
- **Package Variations**: Different weights and dimensions
- **Service Comparison**: All available FedEx services
- **Error Scenarios**: Invalid addresses, API failures

## 📊 Development Stats

- **~1,961 lines** of Python code
- **31 commits** of development history
- **Single-page application** design
- **Real-time API integration**
- **AI-powered tool calling**

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Streamlit** for the amazing web framework
- **LangChain** for AI agent capabilities
- **OpenAI** for GPT integration
- **FedEx** for shipping API access

## 📞 Support

For questions or issues:
1. Check existing [Issues](https://github.com/kikobarr/AI_Shipping_Agent/issues)
2. Create a new issue with detailed description
3. Include error messages and steps to reproduce

---

**Made with ❤️ for the shipping and logistics community**

*Transform your shipping workflow with AI-powered automation!* 🚀
