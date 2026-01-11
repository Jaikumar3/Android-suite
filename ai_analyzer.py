#!/usr/bin/env python3
"""
AI-Powered Security Analyzer for Android Applications
Analyzes decompiled source code for security vulnerabilities

Author: Jai
Version: 1.0.0
"""

import os
import json
import re
import time
from pathlib import Path
from typing import Optional, Dict, List, Tuple

# =============================================================================
# OPTIONAL AI IMPORTS
# =============================================================================

OLLAMA_AVAILABLE = False
OPENAI_AVAILABLE = False

try:
    import requests
    OLLAMA_AVAILABLE = True
except ImportError:
    pass

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    pass


# =============================================================================
# CONFIGURATION
# =============================================================================

class AIConfig:
    """AI Provider Configuration"""
    
    # Ollama settings (local)
    OLLAMA_URL = "http://localhost:11434"
    OLLAMA_MODEL = "llama3.2"  # or codellama, mistral, etc.
    
    # OpenAI API settings
    OPENAI_BASE_URL = None  # None = default OpenAI API
    OPENAI_MODEL = "gpt-4o-mini"
    OPENAI_API_KEY = None  # Set via env var OPENAI_API_KEY
    
    # Siemens AI API settings
    SIEMENS_BASE_URL = "https://api.siemens.com/llm/v1"
    SIEMENS_MODEL = "qwen3-30b-a3b-thinking-2507"  # Options: mistral-7b-instruct, qwen3-30b, etc.
    SIEMENS_MAX_TOKENS = 262144  # Siemens API max context window
    # API Key format: SIAK-your-secret-api-key
    
    # Analysis settings - optimized for Siemens 262K token context
    MAX_FILE_SIZE = 500000  # 500KB max per file (increased for large context)
    MAX_FILES_PER_BATCH = 100  # More files since we have huge context
    CHUNK_SIZE = 50000  # 50K chars per chunk (~12K tokens) - much larger chunks
    MULTI_FILE_BATCH_SIZE = 5  # Analyze multiple files in single request
    
    # Security patterns to prioritize
    PRIORITY_FILES = [
        "MainActivity.java",
        "LoginActivity.java",
        "AuthActivity.java",
        "ApiService.java",
        "NetworkHelper.java",
        "CryptoUtil.java",
        "SharedPreferencesHelper.java",
        "DatabaseHelper.java",
        "WebViewActivity.java",
        "BuildConfig.java",
        "Constants.java",
        "Config.java",
    ]
    
    SECURITY_KEYWORDS = [
        "password", "secret", "api_key", "apikey", "token", "auth",
        "crypto", "cipher", "encrypt", "decrypt", "hash", "md5", "sha",
        "ssl", "tls", "certificate", "pinning", "trust",
        "webview", "javascript", "loadurl", "evaluatejavascript",
        "sharedpreferences", "getsharedpreferences", "edit().put",
        "sqlitedatabase", "rawquery", "execsql",
        "runtime.exec", "processbuilder",
        "intent", "deeplink", "scheme", "exported",
        "root", "su ", "superuser",
        "debug", "log.d", "log.v", "log.i",
    ]
    
    # XML files to SKIP (not security-relevant)
    SKIP_XML_PATTERNS = [
        "res/values-",      # Localization strings (values-es, values-de, etc.)
        "res/drawable",     # Drawable resources (icons, shapes)
        "res/anim",         # Animations
        "res/color",        # Color definitions
        "res/font",         # Font resources
        "res/menu",         # Menu definitions
        "res/mipmap",       # App icons
        "res/navigation",   # Navigation graphs (unless checking deeplinks)
        "res/raw",          # Raw resources
        "res/transition",   # Transition animations
        "res/interpolator", # Animation interpolators
    ]
    
    # XML files to ALWAYS analyze (security-relevant)
    PRIORITY_XML_FILES = [
        "AndroidManifest.xml",
        "network_security_config.xml",
        "strings.xml",           # Main strings (may have API keys)
        "backup_rules.xml",
        "data_extraction_rules.xml",
        "file_paths.xml",
        "provider_paths.xml",
    ]


# =============================================================================
# SECURITY ANALYSIS PROMPTS - Optimized for Siemens 262K Token Context
# =============================================================================

SYSTEM_PROMPT = """You are an elite security researcher and penetration tester specializing in source code security review. Your task is to perform comprehensive static analysis on any source code to identify security vulnerabilities.

## ANALYSIS METHODOLOGY
Perform thorough code review following secure coding best practices. Adapt your analysis based on the programming language detected (Java, Kotlin, Python, JavaScript, Go, XML, Smali, etc.).

## VULNERABILITY CATEGORIES TO ANALYZE

### 1. HARDCODED SECRETS (CWE-798, CWE-259)
Look for in ANY language:
- API keys, passwords, tokens, private keys
- Cloud credentials (AWS, GCP, Azure)
- Database connection strings with credentials
- Encryption keys hardcoded in source
- OAuth/JWT secrets

### 2. INJECTION VULNERABILITIES
**SQL Injection (CWE-89):**
- String concatenation in database queries
- Unsanitized user input in queries
- Missing parameterized queries/prepared statements

**Command Injection (CWE-78):**
- os.system(), subprocess, exec() with user input
- Runtime.exec(), ProcessBuilder with user input
- Shell command construction from user data

**Code Injection (CWE-94):**
- eval(), exec() with user input
- Dynamic code execution
- Template injection
- Deserialization of untrusted data

**XSS (CWE-79):**
- Unsanitized output in HTML/templates
- DOM manipulation with user input
- innerHTML with untrusted data

### 3. INSECURE CRYPTOGRAPHY (CWE-327, CWE-328, CWE-329)
- Weak algorithms: MD5, SHA1, DES, 3DES, RC4
- ECB mode usage
- Hardcoded IVs or keys
- Insecure random number generation
- Missing salt in password hashing
- Weak key lengths

### 4. AUTHENTICATION & SESSION ISSUES (CWE-287, CWE-306)
- Hardcoded credentials
- Weak password policies
- Missing authentication checks
- Insecure session management
- Client-side only authentication
- Missing session timeout

### 5. AUTHORIZATION FLAWS (CWE-862, CWE-863)
- Missing access controls
- IDOR vulnerabilities
- Privilege escalation paths
- Role bypass possibilities

### 6. SENSITIVE DATA EXPOSURE (CWE-200, CWE-312, CWE-532)
- Sensitive data in logs
- Plaintext storage of credentials
- PII exposure
- Debug information in production
- Sensitive data in URLs/query strings

### 7. INSECURE NETWORK COMMUNICATION (CWE-295, CWE-319)
- HTTP instead of HTTPS
- Certificate validation disabled
- SSL/TLS verification bypassed
- Missing certificate pinning
- Cleartext data transmission

### 8. INPUT VALIDATION ISSUES (CWE-20)
- Path traversal
- Open redirects
- XML External Entity (XXE)
- Server-Side Request Forgery (SSRF)
- Regex DoS (ReDoS)

### 9. INSECURE FILE OPERATIONS (CWE-22, CWE-73)
- Path traversal in file operations
- Arbitrary file read/write
- Insecure temp file creation
- File upload vulnerabilities
- Symlink attacks

### 10. ERROR HANDLING & LOGGING (CWE-209, CWE-532)
- Stack traces exposed to users
- Sensitive data in error messages
- Passwords/tokens in logs
- Verbose error messages

### 11. INSECURE DESERIALIZATION (CWE-502)
- Pickle, Marshal with untrusted data
- Java deserialization vulnerabilities
- JSON/XML parsing of untrusted data

### 12. RESOURCE MANAGEMENT (CWE-400, CWE-770)
- Denial of Service vulnerabilities
- Resource exhaustion
- Unbounded operations
- Missing rate limiting

### 13. MOBILE-SPECIFIC (If Android/iOS code)
- Exported components without permissions
- Intent vulnerabilities
- WebView misconfigurations
- Insecure data storage (SharedPreferences, etc.)
- Deep link vulnerabilities
- Tapjacking/overlay attacks

### 14. CONFIGURATION ISSUES
- Debug mode enabled
- Insecure default settings
- Missing security headers
- Overly permissive CORS
- Insecure backup settings

## OUTPUT FORMAT
Return findings in this exact JSON structure:
{
  "findings": [
    {
      "severity": "CRITICAL|HIGH|MEDIUM|LOW|INFO",
      "vulnerability": "Descriptive name of the vulnerability",
      "location": "filename:line_number or function name",
      "code_snippet": "The vulnerable code (1-3 lines)",
      "description": "Detailed explanation of what makes this vulnerable",
      "impact": "What an attacker could achieve by exploiting this",
      "attack_scenario": "Step-by-step how this could be exploited",
      "recommendation": "Specific fix with code example if possible",
      "cwe": "CWE-XXX",
      "cvss_estimate": "0.0-10.0"
    }
  ],
  "summary": "Executive summary of overall security posture",
  "risk_score": 0.0-10.0,
  "critical_count": 0,
  "high_count": 0,
  "medium_count": 0,
  "low_count": 0,
  "recommendations_priority": ["Most critical fix first", "Second priority", "..."]
}

## SEVERITY CLASSIFICATION
- CRITICAL (9.0-10.0): RCE, authentication bypass, hardcoded production secrets
- HIGH (7.0-8.9): SQL injection, XSS, insecure crypto, certificate bypass
- MEDIUM (4.0-6.9): Information disclosure, weak configurations
- LOW (1.0-3.9): Best practice violations, minor issues
- INFO (0.1-0.9): Recommendations, not vulnerabilities

## IMPORTANT INSTRUCTIONS
1. **Detect the language** - Adapt analysis to the specific language/framework
2. Be thorough - analyze every function and class
3. Provide specific line numbers or function names when possible
4. Include actual code snippets showing the vulnerability
5. Give actionable remediation with code examples
6. Consider the context - some patterns are only vulnerable in certain contexts
7. Don't report false positives - only report real security issues

## ANTI-HALLUCINATION RULES (CRITICAL)
You MUST follow these rules strictly to avoid false reports:

1. **ONLY report what you SEE in the code** - Never invent or assume vulnerabilities
2. **Quote EXACT code snippets** - Copy-paste the vulnerable line from the provided code
3. **If unsure, DON'T report it** - When in doubt, leave it out
4. **No hypothetical vulnerabilities** - Don't say "if this were used with user input..."
5. **Verify before reporting**:
   - Is this pattern ACTUALLY in the code? Re-check before adding to findings
   - Can you point to the EXACT line? If not, don't report it
   - Is the code snippet you're quoting REAL? Don't generate fake code
6. **Empty findings are OK** - If no vulnerabilities exist, return empty findings array
7. **Don't inflate severity** - A weak hash for non-sensitive data is LOW, not CRITICAL
8. **Context matters** - MD5 for checksums is fine; MD5 for passwords is not
9. **No speculation** - Don't assume what other files might contain
10. **Be honest** - Say "No security issues found" if the code is secure

FORBIDDEN BEHAVIORS:
- Making up file names or line numbers that don't exist
- Creating fake code snippets that weren't in the input
- Reporting vulnerabilities based on common patterns without seeing them
- Assuming user input reaches a function without evidence
- Reporting the same issue multiple times with different wording

If the code provided is secure or contains only minor issues, report honestly.
A good security analyst knows when to say "this code looks secure."
"""

ANALYSIS_PROMPT = """Analyze this source code for security vulnerabilities. Be thorough and identify all security issues. Detect the programming language and apply appropriate security checks.

File: {filename}

```
{code}
```

Provide comprehensive findings in JSON format as specified in your instructions. Include code snippets, line numbers, and specific remediation steps."""

MULTI_FILE_PROMPT = """Analyze these source files for security vulnerabilities. Look for issues both within individual files and across files (e.g., data flow, authentication bypass).

{files_content}

Provide comprehensive findings in JSON format. Consider cross-file vulnerabilities and data flow issues."""


# =============================================================================
# AI ANALYZER CLASS
# =============================================================================

class AISecurityAnalyzer:
    """AI-powered security analyzer for Android source code"""
    
    def __init__(self, provider: str = "ollama", api_key: Optional[str] = None, 
                 base_url: Optional[str] = None, model: Optional[str] = None,
                 verbose: bool = False):
        """
        Initialize AI analyzer
        
        Args:
            provider: 'ollama' (local) or 'openai' (also works for custom OpenAI-compatible APIs)
            api_key: API key for OpenAI/custom API (not needed for Ollama)
            base_url: Custom API base URL (e.g., Siemens API endpoint)
            model: Override model name
            verbose: Show AI responses for debugging
        """
        self.provider = provider.lower()
        self.api_key = api_key or AIConfig.OPENAI_API_KEY or os.environ.get("OPENAI_API_KEY")
        self.base_url = base_url or AIConfig.OPENAI_BASE_URL
        self.model = model or (AIConfig.OLLAMA_MODEL if self.provider == "ollama" else AIConfig.OPENAI_MODEL)
        self.findings = []
        self.analyzed_files = []
        self.verbose = verbose
        
        # Validate provider
        if self.provider == "ollama" and not OLLAMA_AVAILABLE:
            raise ImportError("requests library required for Ollama. Install: pip install requests")
        if self.provider == "openai" and not OPENAI_AVAILABLE:
            raise ImportError("openai library required. Install: pip install openai")
        if self.provider == "openai" and not self.api_key:
            raise ValueError("API key required. Set OPENAI_API_KEY env var or pass api_key")
    
    def test_api_connection(self) -> Tuple[bool, str]:
        """Test API connection with a simple request"""
        test_prompt = "Reply with only the word 'OK' if you can read this."
        
        try:
            if self.provider == "ollama":
                return self.check_ollama_status()
            else:
                # Test OpenAI/Siemens API
                client_kwargs = {"api_key": self.api_key}
                if self.base_url:
                    client_kwargs["base_url"] = self.base_url
                
                client = openai.OpenAI(**client_kwargs)
                
                response = client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": test_prompt}],
                    max_tokens=10,
                    temperature=0
                )
                
                reply = response.choices[0].message.content
                return True, f"API working! Model: {self.model}, Response: {reply}"
                
        except openai.AuthenticationError as e:
            return False, f"Authentication failed: Invalid API key"
        except openai.NotFoundError as e:
            return False, f"Model not found: {self.model}"
        except openai.RateLimitError as e:
            return False, f"Rate limit exceeded. Try again later."
        except openai.APIConnectionError as e:
            return False, f"Cannot connect to API: {self.base_url or 'OpenAI'}"
        except Exception as e:
            return False, f"API error: {str(e)}"
    
    def check_ollama_status(self) -> Tuple[bool, str]:
        """Check if Ollama is running and model is available"""
        try:
            response = requests.get(f"{AIConfig.OLLAMA_URL}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [m.get("name", "").split(":")[0] for m in models]
                if AIConfig.OLLAMA_MODEL in model_names or any(AIConfig.OLLAMA_MODEL in n for n in model_names):
                    return True, f"Ollama running with {AIConfig.OLLAMA_MODEL}"
                return False, f"Model {AIConfig.OLLAMA_MODEL} not found. Available: {', '.join(model_names)}"
            return False, "Ollama not responding"
        except requests.exceptions.ConnectionError:
            return False, "Ollama not running. Start with: ollama serve"
        except Exception as e:
            return False, f"Error checking Ollama: {e}"
    
    def _call_ollama(self, prompt: str) -> Optional[str]:
        """Call Ollama API"""
        try:
            response = requests.post(
                f"{AIConfig.OLLAMA_URL}/api/generate",
                json={
                    "model": AIConfig.OLLAMA_MODEL,
                    "prompt": f"{SYSTEM_PROMPT}\n\n{prompt}",
                    "stream": False,
                    "options": {
                        "temperature": 0.1,  # Low temp for consistent analysis
                        "num_predict": 4096,
                    }
                },
                timeout=120
            )
            if response.status_code == 200:
                return response.json().get("response", "")
            return None
        except Exception as e:
            print(f"[!] Ollama error: {e}")
            return None
    
    def _call_openai(self, prompt: str) -> Optional[str]:
        """Call OpenAI or compatible API (Siemens, Azure, etc.)"""
        try:
            # Create client with optional custom base URL
            client_kwargs = {"api_key": self.api_key}
            if self.base_url:
                client_kwargs["base_url"] = self.base_url
            
            client = openai.OpenAI(**client_kwargs)
            
            # Determine max_tokens based on provider
            # Siemens API supports up to 262K tokens - use larger response limit
            is_siemens = self.base_url and "siemens.com" in self.base_url
            max_response_tokens = 16384 if is_siemens else 4096
            
            # Build request kwargs
            request_kwargs = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.1,
                "max_tokens": max_response_tokens,
            }
            
            # Only add response_format if using OpenAI (may not be supported by all APIs)
            if not self.base_url:  # Default OpenAI
                request_kwargs["response_format"] = {"type": "json_object"}
            
            response = client.chat.completions.create(**request_kwargs)
            return response.choices[0].message.content
        except Exception as e:
            print(f"[!] API error: {e}")
            return None
    
    def analyze_code(self, code: str, filename: str = "unknown") -> Dict:
        """
        Analyze code snippet for vulnerabilities
        
        Args:
            code: Source code to analyze
            filename: Name of the file being analyzed
            
        Returns:
            Dict with findings
        """
        # Determine chunk size based on provider
        # Siemens API has 262K token limit - can handle much larger code chunks
        is_siemens = self.base_url and "siemens.com" in self.base_url
        chunk_size = AIConfig.CHUNK_SIZE if is_siemens else 8000
        
        # Truncate if too large
        if len(code) > chunk_size:
            code = code[:chunk_size] + "\n// ... truncated ..."
        
        prompt = ANALYSIS_PROMPT.format(filename=filename, code=code)
        
        # Call appropriate provider
        if self.provider == "ollama":
            response = self._call_ollama(prompt)
        else:
            response = self._call_openai(prompt)
        
        if not response:
            return {"error": "No response from AI provider", "findings": []}
        
        # Show response in verbose mode
        if self.verbose:
            print(f"\n  [AI Response] ({len(response)} chars):")
            # Show first 500 chars of response
            preview = response[:500] + "..." if len(response) > 500 else response
            print(f"  {preview}\n")
        
        # Parse JSON response
        try:
            # Extract JSON from response (handle markdown code blocks)
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                result = json.loads(json_match.group())
                # Add filename to findings
                for finding in result.get("findings", []):
                    if "location" not in finding or finding["location"] == "":
                        finding["location"] = filename
                    elif not finding["location"].startswith(filename):
                        finding["location"] = f"{filename}:{finding['location']}"
                
                # Show findings count
                findings_count = len(result.get("findings", []))
                if findings_count > 0:
                    print(f"  [+] Found {findings_count} issue(s)")
                
                return result
            return {"error": "Could not parse JSON", "raw": response, "findings": []}
        except json.JSONDecodeError:
            return {"error": "Invalid JSON response", "raw": response, "findings": []}
    
    def analyze_multiple_files(self, files_content: Dict[str, str]) -> Dict:
        """
        Analyze multiple files in a single API call - leverages large context windows
        
        This is optimized for Siemens API with 262K token context window.
        Sends multiple files together for better cross-file vulnerability detection.
        
        Args:
            files_content: Dict mapping filename to file content
            
        Returns:
            Dict with findings across all files
        """
        # Build combined content
        combined = []
        for filename, content in files_content.items():
            combined.append(f"=== FILE: {filename} ===")
            combined.append(content)
            combined.append("")
        
        files_text = "\n".join(combined)
        
        # Check if this is Siemens API for larger context
        is_siemens = self.base_url and "siemens.com" in self.base_url
        max_chars = 200000 if is_siemens else 30000  # ~50K tokens for Siemens
        
        if len(files_text) > max_chars:
            files_text = files_text[:max_chars] + "\n\n// ... additional files truncated ..."
        
        prompt = MULTI_FILE_PROMPT.format(files_content=files_text)
        
        # Call appropriate provider
        if self.provider == "ollama":
            response = self._call_ollama(prompt)
        else:
            response = self._call_openai(prompt)
        
        if not response:
            return {"error": "No response from AI provider", "findings": []}
        
        # Show response in verbose mode
        if self.verbose:
            print(f"\n  [AI Multi-File Response] ({len(response)} chars):")
            preview = response[:500] + "..." if len(response) > 500 else response
            print(f"  {preview}\n")
        
        # Parse JSON response
        try:
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                result = json.loads(json_match.group())
                return result
            return {"error": "Could not parse JSON", "raw": response, "findings": []}
        except json.JSONDecodeError:
            return {"error": "Invalid JSON response", "raw": response, "findings": []}
    
    def scan_directory(self, directory: str, callback=None) -> List[Dict]:
        """
        Scan a directory of decompiled source code
        
        Args:
            directory: Path to decompiled source (e.g., output/decompiled/jadx)
            callback: Optional callback for progress updates
            
        Returns:
            List of all findings
        """
        self.findings = []
        self.analyzed_files = []
        
        directory = Path(directory)
        if not directory.exists():
            return [{"error": f"Directory not found: {directory}"}]
        
        # Collect source code files (Java, Kotlin, XML, Python, Smali, etc.)
        supported_extensions = ["*.java", "*.kt", "*.xml", "*.py", "*.smali", "*.go", "*.js", "*.ts"]
        source_files = []
        for ext in supported_extensions:
            source_files.extend(directory.rglob(ext))
        
        if not source_files:
            return [{"error": f"No source files found in directory (supported: {', '.join(supported_extensions)})"}]
        
        # Smart XML filtering - skip non-security-relevant resource files
        def is_security_relevant_xml(filepath: Path) -> bool:
            """Check if XML file is worth analyzing"""
            path_str = str(filepath).replace("\\", "/").lower()
            filename = filepath.name.lower()
            
            # Always analyze priority XML files
            if any(p.lower() in filename for p in AIConfig.PRIORITY_XML_FILES):
                return True
            
            # Skip known non-security XML patterns
            if any(skip in path_str for skip in AIConfig.SKIP_XML_PATTERNS):
                return False
            
            # For other XMLs, check if they contain security keywords
            return True  # Default: analyze
        
        # Prioritize security-relevant files
        priority_files = []
        code_files = []  # Java, Kotlin, Smali, Python, etc.
        xml_files = []   # XML files (filtered)
        skipped_xml = 0
        
        for f in source_files:
            # Separate handling for XML vs code files
            if f.suffix.lower() == ".xml":
                if is_security_relevant_xml(f):
                    # Check if it's a priority XML
                    if any(p.lower() in f.name.lower() for p in AIConfig.PRIORITY_XML_FILES):
                        priority_files.append(f)
                    else:
                        xml_files.append(f)
                else:
                    skipped_xml += 1
            else:
                # Code files - check priority
                if any(p.lower() in f.name.lower() for p in AIConfig.PRIORITY_FILES):
                    priority_files.append(f)
                elif self._contains_security_keywords(f):
                    priority_files.append(f)
                else:
                    code_files.append(f)
        
        # Combine: priority first, then code files, then XML
        # This ensures actual source code is analyzed before resource XMLs
        other_files = code_files + xml_files
        
        if skipped_xml > 0:
            print(f"[*] Skipped {skipped_xml} non-security-relevant XML files (drawables, localization, etc.)")
        
        # Combine with priority first - limit to MAX_FILES_PER_BATCH for analysis
        files_to_analyze = priority_files + other_files
        if len(files_to_analyze) > AIConfig.MAX_FILES_PER_BATCH:
            files_to_analyze = files_to_analyze[:AIConfig.MAX_FILES_PER_BATCH]
        
        total = len(files_to_analyze)
        print(f"[*] Analyzing {total} files (prioritized from {len(source_files)} total)")
        
        # Estimate time
        avg_time_per_file = 5  # seconds estimate per file
        estimated_minutes = (total * avg_time_per_file) / 60
        print(f"[*] Estimated time: {estimated_minutes:.1f} minutes (varies by file size and API response)")
        
        # Check if Siemens API - use batch mode for better cross-file analysis
        is_siemens = self.base_url and "siemens.com" in self.base_url
        batch_size = AIConfig.MULTI_FILE_BATCH_SIZE if is_siemens else 1
        
        if is_siemens and batch_size > 1:
            print(f"[*] Siemens API detected - using batch mode ({batch_size} files per request)")
            estimated_minutes = (total / batch_size * 10) / 60  # Batch takes ~10s
            print(f"[*] Batch mode estimated time: {estimated_minutes:.1f} minutes")
        
        consecutive_errors = 0
        max_consecutive_errors = 3  # Stop after 3 consecutive API errors
        auto_save_path = "output/ai_findings_autosave.json"
        start_time = time.time()
        files_processed = 0
        
        try:
            # Process files in batches for Siemens API
            if is_siemens and batch_size > 1:
                batches = [files_to_analyze[i:i + batch_size] for i in range(0, len(files_to_analyze), batch_size)]
                
                for batch_num, batch in enumerate(batches, 1):
                    batch_start = time.time()
                    print(f"\n[Batch {batch_num}/{len(batches)}] Analyzing {len(batch)} files together...")
                    
                    # Collect file contents for batch
                    batch_content = {}
                    for filepath in batch:
                        try:
                            if filepath.stat().st_size > AIConfig.MAX_FILE_SIZE:
                                print(f"  [!] Skipping (too large): {filepath.name}")
                                continue
                            relative_path = filepath.relative_to(directory)
                            batch_content[str(relative_path)] = filepath.read_text(encoding='utf-8', errors='ignore')
                        except Exception as e:
                            print(f"  [!] Error reading {filepath.name}: {e}")
                    
                    if batch_content:
                        print(f"  [*] Sending {len(batch_content)} files to AI API...")
                        result = self.analyze_multiple_files(batch_content)
                        batch_time = time.time() - batch_start
                        
                        if result.get("error"):
                            print(f"  [!] API Error: {result.get('error')}")
                            consecutive_errors += 1
                            if consecutive_errors >= max_consecutive_errors:
                                print(f"\n[!] Stopping: {consecutive_errors} consecutive API errors.")
                                break
                            continue
                        
                        consecutive_errors = 0
                        files_processed += len(batch_content)
                        
                        if result.get("findings"):
                            self.findings.extend(result["findings"])
                            self.analyzed_files.extend(batch_content.keys())
                            print(f"  [+] Found {len(result['findings'])} issue(s) in batch ({batch_time:.1f}s)")
                        else:
                            print(f"  [✓] No issues found in batch ({batch_time:.1f}s)")
                            
                        # Progress update
                        elapsed = time.time() - start_time
                        remaining_batches = len(batches) - batch_num
                        eta = (elapsed / batch_num) * remaining_batches
                        print(f"  [*] Progress: {files_processed}/{total} files | Elapsed: {elapsed:.0f}s | ETA: {eta:.0f}s")
                        
                        # Auto-save after each batch
                        self._auto_save(auto_save_path)
            else:
                # Standard single-file analysis
                for i, filepath in enumerate(files_to_analyze, 1):
                    file_start = time.time()
                    relative_path = filepath.relative_to(directory)
                    
                    if callback:
                        callback(i, total, str(relative_path))
                    else:
                        print(f"[{i}/{total}] Analyzing: {relative_path}")
                    
                    # Skip large files
                    if filepath.stat().st_size > AIConfig.MAX_FILE_SIZE:
                        print(f"  [!] Skipping (too large): {relative_path}")
                        continue
                    
                    try:
                        code = filepath.read_text(encoding='utf-8', errors='ignore')
                        print(f"  [*] Sending to AI API ({len(code)} chars)...")
                        result = self.analyze_code(code, str(relative_path))
                        file_time = time.time() - file_start
                        
                        # Check for API errors
                        if result.get("error"):
                            print(f"  [!] API Error: {result.get('error')} ({file_time:.1f}s)")
                            consecutive_errors += 1
                            if consecutive_errors >= max_consecutive_errors:
                                print(f"\n[!] Stopping: {consecutive_errors} consecutive API errors.")
                                print("[!] Please check your API key and try again.")
                                break
                            continue
                        
                        # Reset error counter on success
                        consecutive_errors = 0
                        files_processed += 1
                        
                        if result.get("findings"):
                            self.findings.extend(result["findings"])
                            self.analyzed_files.append(str(relative_path))
                            print(f"  [+] Found {len(result['findings'])} issue(s) ({file_time:.1f}s)")
                        else:
                            print(f"  [✓] No issues found ({file_time:.1f}s)")
                        
                        # Progress update every 5 files
                        if i % 5 == 0:
                            elapsed = time.time() - start_time
                            avg_per_file = elapsed / i
                            eta = avg_per_file * (total - i)
                            print(f"  [*] Progress: {i}/{total} | Findings: {len(self.findings)} | ETA: {eta:.0f}s")
                        
                        # Auto-save every 5 findings
                        if len(self.findings) % 5 == 0 and self.findings:
                            self._auto_save(auto_save_path)
                            
                    except Exception as e:
                        print(f"  [!] Error analyzing {relative_path}: {e}")
                    
        except KeyboardInterrupt:
            print(f"\n[!] Interrupted by user. Saving {len(self.findings)} findings...")
            self._auto_save(auto_save_path)
            print(f"[+] Auto-saved to: {auto_save_path}")
        
        # Final summary
        total_time = time.time() - start_time
        print(f"\n{'='*50}")
        print(f"[*] ANALYSIS COMPLETE")
        print(f"{'='*50}")
        print(f"  Files processed: {files_processed}/{total}")
        print(f"  Total findings: {len(self.findings)}")
        print(f"  Time taken: {total_time:.1f}s ({total_time/60:.1f} minutes)")
        if files_processed > 0:
            print(f"  Avg per file: {total_time/files_processed:.1f}s")
        
        # Final auto-save
        if self.findings:
            self._auto_save(auto_save_path)
            print(f"  Auto-saved to: {auto_save_path}")
        
        return self.findings
    
    def _auto_save(self, path: str) -> None:
        """Auto-save findings to prevent data loss"""
        try:
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                json.dump({
                    "analyzed_files": self.analyzed_files,
                    "total_findings": len(self.findings),
                    "findings": self.findings,
                    "status": "partial" if len(self.analyzed_files) < AIConfig.MAX_FILES_PER_BATCH else "complete"
                }, f, indent=2)
        except:
            pass  # Silently fail auto-save
    
    def _contains_security_keywords(self, filepath: Path) -> bool:
        """Check if file contains security-relevant keywords"""
        try:
            content = filepath.read_text(encoding='utf-8', errors='ignore').lower()
            return any(kw in content for kw in AIConfig.SECURITY_KEYWORDS[:10])
        except:
            return False
    
    def generate_report(self, output_path: Optional[str] = None) -> str:
        """
        Generate a security report from findings
        
        Args:
            output_path: Optional path to save report
            
        Returns:
            Report as string
        """
        if not self.findings:
            return "No security findings to report."
        
        # Sort by severity
        severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "INFO": 4}
        sorted_findings = sorted(
            self.findings,
            key=lambda x: severity_order.get(x.get("severity", "INFO"), 5)
        )
        
        # Count by severity
        severity_counts = {}
        for f in sorted_findings:
            sev = f.get("severity", "INFO")
            severity_counts[sev] = severity_counts.get(sev, 0) + 1
        
        # Build report
        report = []
        report.append("=" * 70)
        report.append("AI SECURITY ANALYSIS REPORT")
        report.append("Android Source Code Analysis")
        report.append("=" * 70)
        report.append("")
        report.append("SUMMARY")
        report.append("-" * 40)
        report.append(f"Files Analyzed: {len(self.analyzed_files)}")
        report.append(f"Total Findings: {len(sorted_findings)}")
        report.append("")
        
        for sev in ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]:
            if sev in severity_counts:
                emoji = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🟢", "INFO": "🔵"}.get(sev, "")
                report.append(f"  {emoji} {sev}: {severity_counts[sev]}")
        
        report.append("")
        report.append("=" * 70)
        report.append("DETAILED FINDINGS")
        report.append("=" * 70)
        
        for i, finding in enumerate(sorted_findings, 1):
            sev = finding.get("severity", "INFO")
            emoji = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🟢", "INFO": "🔵"}.get(sev, "")
            
            report.append("")
            report.append(f"[{i}] {emoji} {sev}: {finding.get('vulnerability', 'Unknown')}")
            report.append("-" * 50)
            report.append(f"Location: {finding.get('location', 'Unknown')}")
            report.append(f"Description: {finding.get('description', 'N/A')}")
            report.append(f"Impact: {finding.get('impact', 'N/A')}")
            report.append(f"Recommendation: {finding.get('recommendation', 'N/A')}")
            if finding.get("cwe"):
                report.append(f"CWE: {finding.get('cwe')}")
        
        report.append("")
        report.append("=" * 70)
        report.append("END OF REPORT")
        report.append("=" * 70)
        
        report_text = "\n".join(report)
        
        # Save if path provided
        if output_path:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report_text)
            print(f"[+] Report saved to: {output_path}")
        
        return report_text
    
    def export_json(self, output_path: str) -> None:
        """Export findings as JSON"""
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump({
                "analyzed_files": self.analyzed_files,
                "total_findings": len(self.findings),
                "findings": self.findings
            }, f, indent=2)
        print(f"[+] JSON exported to: {output_path}")


# =============================================================================
# QUICK ANALYSIS FUNCTIONS
# =============================================================================

def quick_analyze_file(filepath: str, provider: str = "ollama") -> Dict:
    """Quick analyze a single file"""
    analyzer = AISecurityAnalyzer(provider=provider)
    code = Path(filepath).read_text(encoding='utf-8', errors='ignore')
    return analyzer.analyze_code(code, Path(filepath).name)


def quick_analyze_directory(directory: str, provider: str = "ollama") -> str:
    """Quick analyze a directory and return report"""
    analyzer = AISecurityAnalyzer(provider=provider)
    analyzer.scan_directory(directory)
    return analyzer.generate_report()


# =============================================================================
# CLI INTERFACE (for standalone usage)
# =============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="AI Security Analyzer for Android Source Code")
    parser.add_argument("path", help="Path to decompiled source directory or single file")
    parser.add_argument("--provider", "-p", choices=["ollama", "openai"], default="ollama",
                       help="AI provider (default: ollama)")
    parser.add_argument("--output", "-o", help="Output report path")
    parser.add_argument("--json", "-j", help="Export findings as JSON")
    parser.add_argument("--model", "-m", help="Override model name")
    
    args = parser.parse_args()
    
    if args.model:
        AIConfig.OLLAMA_MODEL = args.model
        AIConfig.OPENAI_MODEL = args.model
    
    print(f"[*] AI Security Analyzer - Using {args.provider}")
    
    try:
        analyzer = AISecurityAnalyzer(provider=args.provider)
        
        # Check Ollama status if using it
        if args.provider == "ollama":
            ok, msg = analyzer.check_ollama_status()
            print(f"[{'+'if ok else '!'}] {msg}")
            if not ok:
                exit(1)
        
        path = Path(args.path)
        
        if path.is_file():
            print(f"[*] Analyzing single file: {path}")
            result = quick_analyze_file(str(path), args.provider)
            print(json.dumps(result, indent=2))
        else:
            print(f"[*] Scanning directory: {path}")
            analyzer.scan_directory(str(path))
            
            # Generate report
            report = analyzer.generate_report(args.output)
            if not args.output:
                print(report)
            
            # Export JSON if requested
            if args.json:
                analyzer.export_json(args.json)
                
    except Exception as e:
        print(f"[!] Error: {e}")
        exit(1)
