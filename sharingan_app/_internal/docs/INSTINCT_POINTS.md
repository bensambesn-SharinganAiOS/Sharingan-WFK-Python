# Sharingan OS - Points de Vérification des Instincts

## 📍 LES 5 POINTS D'INSTINCT DANS LE CODE

```
┌─────────────────────────────────────────────────────────────────┐
│              FLUX D'UNE REQUÊTE UTILISATEUR                     │
└─────────────────────────────────────────────────────────────────┘

     1. CONSCIOUSNESS ANALYZE
        ↓
     2. CONTEXT BUILD
        ↓
     3. AI RESPONSE
        ↓
     4. TOOL EXECUTION
        ↓
     5. RESULT RECORDING → GENOME
```

---

## 📍 POINT 1: SYSTEM_CONSCIOUSNESS.ANALYZE_QUERY()

**Fichier**: `system_consciousness.py`
**Quand**: Avant de décider ce que l'utilisateur veut

```python
def analyze_query(self, query: str) -> Dict:
    """Analyse query avec instinct pré-check"""
    
    # 1. Vérifier instinct immediately
    from genome_memory import get_genome_memory
    genome = get_genome_memory()
    instinct_match = genome.match_instinct(query)
    
    if instinct_match:
        return {
            "intent": "instinct_response",
            "response": instinct_match['response'],
            "source": "genome_instinct",
            "confidence": instinct_match.get('success_rate', 0.5)
        }
    
    # 2. Vérifier patterns d'échec connus
    failure_pattern = genome.find_genes(
        category="failure_patterns",
        min_priority=80
    )
    
    for gene in failure_pattern:
        if gene.key in query.lower():
            return {
                "intent": "warning",
                "message": f"Note: Cette approche a échoué avant avec {gene.key}",
                "gene_key": gene.key,
                "source": "genome_experience"
            }
    
    # 3. Continue avec l'analyse normale
    return self._perform_analysis(query)
```

---

## 📍 POINT 2: CONTEXT_MANAGER.ADD_MESSAGE()

**Fichier**: `context_manager.py`
**Quand**: Avant d'ajouter un message au contexte

```python
def add_message(self, role: str, content: str, 
                metadata: Optional[Dict] = None) -> int:
    """Add message avec instinct de contexte"""
    
    # Vérifier instinct contextuel
    genome = get_genome_memory()
    
    # Si c'est un message utilisateur
    if role == "user":
        # Chercher pattern de préférence utilisateur
        pref = genome.get_gene(f"user_preference_{content[:30]}", "knowledge")
        if pref:
            # Adapter le contexte selon préférence
            self._apply_user_preferences(pref.data)
    
    # Enregistrer l'expérience
    genome.record_success("context_interaction")
    
    return super().add_message(role, content, metadata)
```

---

## 📍 POINT 3: AI_PROVIDERS.CHAT()

**Fichier**: `ai_providers.py`
**Quand**: Avant que l'IA génère une réponse

```python
def chat(self, message: str, provider: str = None, 
         context: List[Dict] = None) -> Dict:
    """Chat avec instinct pré-optimisation"""
    
    genome = get_genome_memory()
    
    # 1. Optimiser le prompt selon expérience
    optimized_message = message
    
    # Chercher si on a des patterns qui marchent pour ce type de query
    success_patterns = genome.find_genes(
        category="prompt_patterns",
        min_priority=70
    )
    
    for gene in success_patterns:
        if gene.key in message.lower():
            optimized_message = gene.data.get("optimized_prompt", message)
            break
    
    # 2. Vérifier provider preference
    provider_pref = genome.get_gene(f"provider_{message[:20]}", "knowledge")
    if provider_pref:
        preferred_provider = provider_pref.data.get("best_provider")
        if preferred_provider:
            provider = preferred_provider
    
    # 3. Générer réponse
    result = self._generate(optimized_message, provider, context)
    
    # 4. Enregistrer succès
    genome.record_success(f"ai_response_{provider}")
    
    return result
```

---

## 📍 POINT 4: TOOL_REGISTRY.EXECUTE()

**Fichier**: `tool_registry.py` (à créer ou modifier)
**Quand**: Avant d'exécuter un outil

```python
def execute_tool(self, tool_name: str, **kwargs) -> Dict:
    """Exécute un outil avec instinct de prevention"""
    
    genome = get_genome_memory()
    tool_key = f"tool_{tool_name}"
    
    # 1. Vérifier expériences précédentes de cet outil
    tool_exp = genome.get_gene(tool_key, "experience")
    
    if tool_exp:
        # Si l'outil a des patterns d'échec connus
        if tool_exp.data.get("has_failures"):
            failure_conditions = tool_exp.data.get("failure_conditions", [])
            
            for condition in failure_conditions:
                if self._check_condition(condition, kwargs):
                    return {
                        "status": "skipped_by_instinct",
                        "reason": f"Instinct: {condition['reason']}",
                        "alternative": condition.get("alternative"),
                        "source": "genome_experience"
                    }
    
    # 2. Exécuter l'outil normalement
    result = self._run_tool(tool_name, **kwargs)
    
    # 3. Enregistrer le résultat
    if result.get("success"):
        genome.record_success(tool_key)
        genome.mutate(tool_key, {
            "last_success": datetime.now().isoformat(),
            "success_count": tool_exp.data.get("success_count", 0) + 1
        }, "experience", source="tool_execution")
    else:
        genome.record_failure(tool_key)
        # Enregistrer les conditions d'échec pour instinct futur
        self._record_failure_conditions(tool_name, result, kwargs)
    
    return result
```

---

## 📍 POINT 5: MAIN.RESPONSE_POST_PROCESSING()

**Fichier**: `main.py` ou `sharingan_os.py`
**Quand**: Après avoir reçu une réponse de l'IA ou outil

```python
def post_process_response(self, response: Dict, query: str) -> Dict:
    """Post-processing avec instinct d'amélioration"""
    
    genome = get_genome_memory()
    
    # 1. Vérifier si la réponse est satisfaisante
    if response.get("success") and not response.get("error"):
        genome.record_success("response_quality")
        
        # Enregistrer les patterns qui ont marché
        if "tool_used" in response:
            tool = response["tool_used"]
            genome.mutate(f"success_{tool}", {
                "context": query,
                "result_summary": response.get("summary", "")[:200]
            }, "success_patterns", source="response_post_process")
    
    # 2. Si erreurs, enregistrer pour éviter futur
    elif response.get("error"):
        genome.record_failure("response_quality")
        
        # Créer un pattern d'échec
        genome.mutate(f"failure_{hash(query)}", {
            "query_pattern": query[:100],
            "error": response.get("error"),
            "timestamp": datetime.now().isoformat()
        }, "failure_patterns", source="response_post_process")
    
    return response
```

---

## 📊 RÉSUMÉ DES 5 POINTS

| # | Fichier | Fonction | Type d'instinct |
|---|---------|----------|-----------------|
| 1 | `system_consciousness.py` | `analyze_query()` | Pattern match, warning |
| 2 | `context_manager.py` | `add_message()` | Préférences utilisateur |
| 3 | `ai_providers.py` | `chat()` | Optimisation prompt |
| 4 | `tool_registry.py` | `execute_tool()` | Prévention échec outil |
| 5 | `main.py` | `post_process_response()` | Enregistrer résultat |

---

## 🚀 PROCHAINES ÉTAPES

1. Créer les functions dans chaque fichier
2. Connecter `genome_memory.py` à chaque point
3. Tester avec un cas simple
4. Observer l'évolution du genome

---

*Document créé le 2026-01-11*
