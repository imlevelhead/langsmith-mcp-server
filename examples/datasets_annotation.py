from typing import Any, Dict, List, Optional
import os
import sys
import json
import uuid
from datetime import datetime

from langsmith import Client
from langsmith.schemas import DataType
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("LANGSMITH_API_KEY")

if not api_key:
    print("Warning: LANGSMITH_API_KEY not found in environment variables")
    print("Some operations may fail without proper authentication")

client = Client(api_key=api_key)

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))


def test_datasets_operations() -> Dict[str, Any]:
    """
    Test all dataset-related operations including creation, listing, reading, and deletion.
    
    Returns:
        Dictionary containing test results for all dataset operations
    """
    results = {"datasets": {}}
    
    try:
        # 1. List existing datasets
        print("Testing dataset listing...")
        datasets = list(client.list_datasets(limit=5))
        results["datasets"]["list_existing"] = {
            "count": len(datasets),
            "dataset_names": [d.name for d in datasets] if datasets else []
        }
        print(f"Found {len(datasets)} existing datasets")
        
        # 2. Create a new dataset
        print("Testing dataset creation...")
        dataset_name = f"test-dataset-{uuid.uuid4().hex[:8]}"
        new_dataset = client.create_dataset(
            dataset_name=dataset_name,
            description="Test dataset created by API testing script",
            data_type=DataType.kv
        )
        results["datasets"]["create"] = {
            "success": True,
            "dataset_id": str(new_dataset.id),
            "dataset_name": new_dataset.name,
            "data_type": new_dataset.data_type
        }
        print(f"Created dataset: {new_dataset.name} (ID: {new_dataset.id})")
        
        # 3. Read the created dataset
        print("Testing dataset reading...")
        read_dataset = client.read_dataset(dataset_id=new_dataset.id)
        results["datasets"]["read"] = {
            "success": True,
            "dataset_id": str(read_dataset.id),
            "dataset_name": read_dataset.name,
            "description": read_dataset.description,
            "data_type": read_dataset.data_type,
            "created_at": str(read_dataset.created_at)
        }
        print(f"Read dataset: {read_dataset.name}")
        
        # 4. Check if dataset exists
        print("Testing dataset existence check...")
        exists = client.has_dataset(dataset_name=dataset_name)
        results["datasets"]["exists"] = {
            "success": True,
            "dataset_name": dataset_name,
            "exists": exists
        }
        print(f"Dataset {dataset_name} exists: {exists}")
        
        # 5. List dataset versions
        print("Testing dataset versions...")
        versions = list(client.list_dataset_versions(dataset_id=new_dataset.id))
        results["datasets"]["versions"] = {
            "count": len(versions),
            "version_ids": [str(v.id) for v in versions] if versions else []
        }
        print(f"Found {len(versions)} versions for dataset")
        
        # 6. List dataset splits
        print("Testing dataset splits...")
        splits = list(client.list_dataset_splits(dataset_id=new_dataset.id))
        results["datasets"]["splits"] = {
            "count": len(splits),
            "split_names": [s.name for s in splits] if splits else []
        }
        print(f"Found {len(splits)} splits for dataset")
        
        # 7. Update dataset tag
        print("Testing dataset tag update...")
        from datetime import datetime
        client.update_dataset_tag(dataset_id=new_dataset.id, tag="test-tag", as_of=datetime.now())
        results["datasets"]["update_tag"] = {"success": True}
        print("Updated dataset tag")
        
        # 8. Delete the test dataset
        print("Testing dataset deletion...")
        client.delete_dataset(dataset_id=new_dataset.id)
        results["datasets"]["delete"] = {"success": True}
        print(f"Deleted dataset: {dataset_name}")
        
    except Exception as e:
        results["datasets"]["error"] = f"Dataset operations failed: {str(e)}"
        print(f"Dataset operations error: {str(e)}")
    
    return results


def test_examples_operations() -> Dict[str, Any]:
    """
    Test all example-related operations including creation, listing, reading, and deletion.
    
    Returns:
        Dictionary containing test results for all example operations
    """
    results = {"examples": {}}
    
    try:
        # First create a dataset to work with
        dataset_name = f"test-examples-dataset-{uuid.uuid4().hex[:8]}"
        dataset = client.create_dataset(
            dataset_name=dataset_name,
            description="Test dataset for examples operations",
            data_type=DataType.kv
        )
        
        # 1. Create a simple example
        print("Testing example creation...")
        example = client.create_example(
            dataset_id=dataset.id,
            inputs={"question": "What is the capital of France?"},
            outputs={"answer": "The capital of France is Paris."},
            metadata={"source": "test-script", "difficulty": "easy"}
        )
        results["examples"]["create_simple"] = {
            "success": True,
            "example_id": str(example.id),
            "inputs": example.inputs,
            "outputs": example.outputs
        }
        print(f"Created example: {example.id}")
        
        # 2. Create a chat example
        print("Testing chat example creation...")
        chat_example = client.create_chat_example(
            dataset_id=dataset.id,
            messages=[
                {"role": "user", "content": "Hello, how are you?"},
                {"role": "assistant", "content": "I'm doing well, thank you for asking!"}
            ]
        )
        results["examples"]["create_chat"] = {
            "success": True,
            "example_id": str(chat_example.id),
            "message_count": len(chat_example.messages) if hasattr(chat_example, 'messages') else 0
        }
        print(f"Created chat example: {chat_example.id}")
        
        # 3. Create an LLM example
        print("Testing LLM example creation...")
        llm_example = client.create_llm_example(
            dataset_id=dataset.id,
            prompt="Translate 'Hello world' to Spanish",
            generation="Hola mundo"
        )
        results["examples"]["create_llm"] = {
            "success": True,
            "example_id": str(llm_example.id),
            "inputs": llm_example.inputs,
            "outputs": llm_example.outputs
        }
        print(f"Created LLM example: {llm_example.id}")
        
        # 4. List examples
        print("Testing example listing...")
        examples = list(client.list_examples(dataset_id=dataset.id, limit=10))
        results["examples"]["list"] = {
            "count": len(examples),
            "example_ids": [str(e.id) for e in examples]
        }
        print(f"Found {len(examples)} examples in dataset")
        
        # 5. Read a specific example
        print("Testing example reading...")
        if examples:
            read_example = client.read_example(example_id=examples[0].id)
            results["examples"]["read"] = {
                "success": True,
                "example_id": str(read_example.id),
                "inputs": read_example.inputs,
                "outputs": read_example.outputs,
                "metadata": read_example.metadata
            }
            print(f"Read example: {read_example.id}")
        
        # 6. Update an example
        print("Testing example update...")
        if examples:
            try:
                updated_example = client.update_example(
                    example_id=examples[0].id,
                    inputs={"question": "What is the capital of France? (updated)"},
                    outputs={"answer": "The capital of France is Paris. (updated)"},
                    metadata={"source": "test-script", "difficulty": "easy", "updated": True}
                )
                # Handle both dict and object responses
                if isinstance(updated_example, dict):
                    results["examples"]["update"] = {
                        "success": True,
                        "example_id": str(updated_example.get("id", examples[0].id)),
                        "inputs": updated_example.get("inputs", {}),
                        "outputs": updated_example.get("outputs", {})
                    }
                else:
                    results["examples"]["update"] = {
                        "success": True,
                        "example_id": str(updated_example.id),
                        "inputs": updated_example.inputs,
                        "outputs": updated_example.outputs
                    }
                print(f"Updated example: {examples[0].id}")
            except Exception as e:
                results["examples"]["update"] = {
                    "success": False,
                    "error": str(e)
                }
                print(f"Failed to update example: {str(e)}")
        
        # 7. Create multiple examples at once
        print("Testing bulk example creation...")
        try:
            bulk_examples = [
                {
                    "inputs": {"question": f"Question {i}"},
                    "outputs": {"answer": f"Answer {i}"},
                    "metadata": {"batch": "bulk", "index": i}
                }
                for i in range(3)
            ]
            created_examples = client.create_examples(
                dataset_id=dataset.id,
                examples=bulk_examples
            )
            # Handle both list of objects and other response types
            if isinstance(created_examples, list):
                example_ids = [str(e.id) if hasattr(e, 'id') else str(e.get('id', 'unknown')) for e in created_examples]
            else:
                example_ids = [str(created_examples.id) if hasattr(created_examples, 'id') else 'unknown']
            
            results["examples"]["create_bulk"] = {
                "success": True,
                "count": len(created_examples) if isinstance(created_examples, list) else 1,
                "example_ids": example_ids
            }
            print(f"Created {len(created_examples) if isinstance(created_examples, list) else 1} examples in bulk")
        except Exception as e:
            results["examples"]["create_bulk"] = {
                "success": False,
                "error": str(e)
            }
            print(f"Failed to create bulk examples: {str(e)}")
        
        # 8. Delete examples
        print("Testing example deletion...")
        if examples:
            client.delete_example(example_id=examples[0].id)
            results["examples"]["delete_single"] = {"success": True}
            print(f"Deleted example: {examples[0].id}")
        
        # Clean up the dataset
        client.delete_dataset(dataset_id=dataset.id)
        print(f"Cleaned up dataset: {dataset_name}")
        
    except Exception as e:
        results["examples"]["error"] = f"Example operations failed: {str(e)}"
        print(f"Example operations error: {str(e)}")
    
    return results


def test_annotation_queues_operations() -> Dict[str, Any]:
    """
    Test all annotation queue-related operations including creation, listing, reading, and deletion.
    
    Returns:
        Dictionary containing test results for all annotation queue operations
    """
    results = {"annotation_queues": {}}
    test_runs = []  # Declare at function level
    
    try:
        # 1. List existing annotation queues
        print("Testing annotation queue listing...")
        queues = list(client.list_annotation_queues(limit=5))
        results["annotation_queues"]["list_existing"] = {
            "count": len(queues),
            "queue_names": [q.name for q in queues] if queues else []
        }
        print(f"Found {len(queues)} existing annotation queues")
        
        # 2. Create a new annotation queue
        print("Testing annotation queue creation...")
        queue_name = f"test-queue-{uuid.uuid4().hex[:8]}"
        new_queue = client.create_annotation_queue(
            name=queue_name,
            description="Test annotation queue created by API testing script"
        )
        results["annotation_queues"]["create"] = {
            "success": True,
            "queue_id": str(new_queue.id),
            "queue_name": new_queue.name,
            "description": new_queue.description
        }
        print(f"Created annotation queue: {new_queue.name} (ID: {new_queue.id})")
        
        # 3. Read the created annotation queue
        print("Testing annotation queue reading...")
        read_queue = client.read_annotation_queue(queue_id=new_queue.id)
        results["annotation_queues"]["read"] = {
            "success": True,
            "queue_id": str(read_queue.id),
            "queue_name": read_queue.name,
            "description": read_queue.description,
            "created_at": str(read_queue.created_at)
        }
        print(f"Read annotation queue: {read_queue.name}")
        
        # 4. Update the annotation queue
        print("Testing annotation queue update...")
        try:
            updated_queue = client.update_annotation_queue(
                queue_id=new_queue.id,
                name=f"{queue_name}-updated",
                description="Updated test annotation queue description"
            )
            results["annotation_queues"]["update"] = {
                "success": True,
                "queue_id": str(updated_queue.id) if updated_queue and hasattr(updated_queue, 'id') else str(new_queue.id),
                "queue_name": updated_queue.name if updated_queue and hasattr(updated_queue, 'name') else f"{queue_name}-updated",
                "description": updated_queue.description if updated_queue and hasattr(updated_queue, 'description') else "Updated test annotation queue description"
            }
            print(f"Updated annotation queue: {queue_name}-updated")
        except Exception as e:
            results["annotation_queues"]["update"] = {
                "success": False,
                "error": str(e)
            }
            print(f"Failed to update annotation queue: {str(e)}")
        
        # 5. Add runs to annotation queue (if we have any runs)
        print("Testing adding runs to annotation queue...")
        try:
            # Try different approaches to get existing runs
            print("Looking for existing runs...")
            
            # First, let's see what projects are available
            try:
                projects = list(client.list_projects(limit=5))
                print(f"Found {len(projects)} projects: {[p.name for p in projects]}")
                
                existing_runs = []
                if projects:
                    # Check all projects for runs
                    for project in projects:
                        try:
                            project_runs = list(client.list_runs(project_name=project.name, limit=5))
                            if project_runs:
                                print(f"Found {len(project_runs)} runs in project '{project.name}'")
                                existing_runs = project_runs
                                break
                            else:
                                print(f"No runs found in project '{project.name}'")
                        except Exception as e:
                            print(f"Failed to list runs from project '{project.name}': {str(e)}")
                            continue
                else:
                    print("No projects found")
                    
            except Exception as e1:
                print(f"Failed to list projects: {str(e1)}")
                try:
                    # Try listing runs with a session filter
                    existing_runs = list(client.list_runs(session_id="test", limit=5))
                    print(f"Found {len(existing_runs)} runs in test session")
                except Exception as e2:
                    print(f"Failed to list runs with session filter: {str(e2)}")
                    try:
                        # Try listing runs with a trace filter
                        existing_runs = list(client.list_runs(trace_id="test", limit=5))
                        print(f"Found {len(existing_runs)} runs in test trace")
                    except Exception as e3:
                        print(f"Failed to list runs with trace filter: {str(e3)}")
                        # Try listing all runs without filters
                        existing_runs = list(client.list_runs(limit=5))
                        print(f"Found {len(existing_runs)} runs without filters")
            
            if existing_runs:
                # Print details of the first few runs
                for i, run in enumerate(existing_runs[:3]):
                    print(f"Run {i+1}: ID={run.id}, Name={getattr(run, 'name', 'N/A')}, Type={getattr(run, 'run_type', 'N/A')}")
                
                # Use the first few existing runs
                run_ids = [str(run.id) for run in existing_runs[:2]]
                print(f"Attempting to add runs: {run_ids}")
                
                client.add_runs_to_annotation_queue(
                    queue_id=new_queue.id,
                    run_ids=run_ids
                )
                results["annotation_queues"]["add_runs"] = {
                    "success": True,
                    "run_count": len(run_ids),
                    "run_ids": run_ids
                }
                print(f"Added {len(run_ids)} existing runs to annotation queue")
            else:
                results["annotation_queues"]["add_runs"] = {
                    "success": False,
                    "reason": "No existing runs found in the system"
                }
                print("No existing runs found in the system")
        except Exception as e:
            results["annotation_queues"]["add_runs"] = {
                "success": False,
                "error": str(e)
            }
            print(f"Failed to add runs to annotation queue: {str(e)}")
        
        # 6. Get runs from annotation queue
        print("Testing getting runs from annotation queue...")
        try:
            # Try to get the first run from the queue (index 0)
            queue_run = client.get_run_from_annotation_queue(
                queue_id=new_queue.id,
                index=0
            )
            results["annotation_queues"]["get_runs"] = {
                "success": True,
                "run_id": str(queue_run.id) if hasattr(queue_run, 'id') else "unknown",
                "run_type": queue_run.run_type if hasattr(queue_run, 'run_type') else "unknown"
            }
            print(f"Retrieved run from annotation queue: {queue_run.id if hasattr(queue_run, 'id') else 'unknown'}")
        except Exception as e:
            results["annotation_queues"]["get_runs"] = {
                "success": False,
                "error": str(e)
            }
            print(f"Failed to get runs from annotation queue: {str(e)}")
        
        # 7. Delete runs from annotation queue
        print("Testing deleting runs from annotation queue...")
        try:
            # Use the same approach as adding runs - find existing runs from projects
            existing_runs_for_delete = []
            if projects:
                for project in projects:
                    try:
                        project_runs = list(client.list_runs(project_name=project.name, limit=1))
                        if project_runs:
                            existing_runs_for_delete = project_runs
                            break
                    except Exception as e:
                        continue
            
            if existing_runs_for_delete:
                client.delete_run_from_annotation_queue(
                    queue_id=new_queue.id,
                    run_id=existing_runs_for_delete[0].id
                )
                results["annotation_queues"]["delete_run"] = {"success": True}
                print(f"Deleted run {existing_runs_for_delete[0].id} from annotation queue")
            else:
                results["annotation_queues"]["delete_run"] = {
                    "success": False,
                    "reason": "No runs available to delete"
                }
                print("No runs available to delete from annotation queue")
        except Exception as e:
            results["annotation_queues"]["delete_run"] = {
                "success": False,
                "error": str(e)
            }
            print(f"Failed to delete run from annotation queue: {str(e)}")
        
        # 8. Delete the annotation queue
        print("Testing annotation queue deletion...")
        client.delete_annotation_queue(queue_id=new_queue.id)
        results["annotation_queues"]["delete"] = {"success": True}
        print(f"Deleted annotation queue: {queue_name}-updated")
        
    except Exception as e:
        results["annotation_queues"]["error"] = f"Annotation queue operations failed: {str(e)}"
        print(f"Annotation queue operations error: {str(e)}")
    
    return results


def test_dataset_advanced_operations() -> Dict[str, Any]:
    """
    Test advanced dataset operations like uploading CSV, dataframes, and dataset sharing.
    
    Returns:
        Dictionary containing test results for advanced dataset operations
    """
    results = {"advanced_datasets": {}}
    
    try:
        # 1. Test CSV upload (create a simple CSV in memory)
        print("Testing CSV upload...")
        import io
        csv_content = "question,answer\nWhat is 2+2?,4\nWhat is the capital of France?,Paris"
        csv_file = ("test_data.csv", io.BytesIO(csv_content.encode('utf-8')))
        
        csv_dataset = client.upload_csv(
            csv_file=csv_file,
            input_keys=["question"],
            output_keys=["answer"],
            name=f"test-csv-dataset-{uuid.uuid4().hex[:8]}",
            description="Test dataset created from CSV upload",
            data_type=DataType.kv
        )
        results["advanced_datasets"]["csv_upload"] = {
            "success": True,
            "dataset_id": str(csv_dataset.id),
            "dataset_name": csv_dataset.name
        }
        print(f"Created dataset from CSV: {csv_dataset.name}")
        
        # 2. Test dataframe upload
        print("Testing dataframe upload...")
        import pandas as pd
        
        df_data = {
            "input_text": ["Hello", "World", "Test"],
            "output_text": ["Hi", "Earth", "Check"]
        }
        df = pd.DataFrame(df_data)
        
        df_dataset = client.upload_dataframe(
            df=df,
            name=f"test-df-dataset-{uuid.uuid4().hex[:8]}",
            input_keys=["input_text"],
            output_keys=["output_text"],
            description="Test dataset created from dataframe upload"
        )
        results["advanced_datasets"]["dataframe_upload"] = {
            "success": True,
            "dataset_id": str(df_dataset.id),
            "dataset_name": df_dataset.name
        }
        print(f"Created dataset from dataframe: {df_dataset.name}")
        
        # 3. Test dataset sharing
        print("Testing dataset sharing...")
        try:
            share_result = client.share_dataset(dataset_id=csv_dataset.id)
            print(f"Share result type: {type(share_result)}")
            print(f"Share result attributes: {dir(share_result) if hasattr(share_result, '__dict__') else 'No attributes'}")
            
            share_token = None
            if hasattr(share_result, 'share_token'):
                share_token = share_result.share_token
            elif hasattr(share_result, 'token'):
                share_token = share_result.token
            elif isinstance(share_result, dict):
                share_token = share_result.get('share_token') or share_result.get('token')
            
            results["advanced_datasets"]["share"] = {
                "success": True,
                "dataset_id": str(csv_dataset.id),
                "share_token": share_token,
                "shared": True
            }
            print(f"Shared dataset: {csv_dataset.name}, Token: {share_token}")
        except Exception as e:
            results["advanced_datasets"]["share"] = {
                "success": False,
                "error": str(e)
            }
            print(f"Failed to share dataset: {str(e)}")
        
        # 4. Test reading shared dataset (requires share token)
        print("Testing reading shared dataset...")
        try:
            if results["advanced_datasets"]["share"]["success"] and results["advanced_datasets"]["share"]["share_token"]:
                read_shared = client.read_shared_dataset(share_token=results["advanced_datasets"]["share"]["share_token"])
                results["advanced_datasets"]["read_shared"] = {
                    "success": True,
                    "dataset_id": str(read_shared.id),
                    "dataset_name": read_shared.name
                }
                print(f"Read shared dataset: {read_shared.name}")
            else:
                results["advanced_datasets"]["read_shared"] = {
                    "success": False,
                    "error": "No share token available"
                }
                print("No share token available for reading shared dataset")
        except Exception as e:
            results["advanced_datasets"]["read_shared"] = {
                "success": False,
                "error": str(e)
            }
            print(f"Failed to read shared dataset: {str(e)}")
        
        # 5. Test unsharing dataset
        print("Testing dataset unsharing...")
        try:
            client.unshare_dataset(dataset_id=csv_dataset.id)
            results["advanced_datasets"]["unshare"] = {
                "success": True,
                "dataset_id": str(csv_dataset.id),
                "shared": False
            }
            print(f"Unshared dataset: {csv_dataset.name}")
        except Exception as e:
            results["advanced_datasets"]["unshare"] = {
                "success": False,
                "error": str(e)
            }
            print(f"Failed to unshare dataset: {str(e)}")
        
        # 6. Test dataset versioning
        print("Testing dataset versioning...")
        try:
            versions = list(client.list_dataset_versions(dataset_id=csv_dataset.id))
            version_info = []
            for v in versions:
                try:
                    version_info.append({
                        "version": str(getattr(v, 'version', 'unknown')),
                        "created_at": str(getattr(v, 'created_at', 'unknown'))
                    })
                except Exception:
                    version_info.append({"version": "unknown", "created_at": "unknown"})
            
            results["advanced_datasets"]["versioning"] = {
                "success": True,
                "version_count": len(versions),
                "version_info": version_info
            }
            print(f"Found {len(versions)} versions for dataset")
        except Exception as e:
            results["advanced_datasets"]["versioning"] = {
                "success": False,
                "error": str(e)
            }
            print(f"Failed to get dataset versions: {str(e)}")
        
        # Clean up
        client.delete_dataset(dataset_id=csv_dataset.id)
        client.delete_dataset(dataset_id=df_dataset.id)
        print("Cleaned up advanced test datasets")
        
    except Exception as e:
        results["advanced_datasets"]["error"] = f"Advanced dataset operations failed: {str(e)}"
        print(f"Advanced dataset operations error: {str(e)}")
    
    return results


def main():
    """
    Main function to run all tests for datasets, examples, and annotation queues.
    """
    print("Starting LangSmith API Testing for Datasets, Examples, and Annotation Queues")
    print("=" * 80)
    
    all_results = {
        "timestamp": datetime.now().isoformat(),
        "api_key_configured": bool(api_key)
    }
    
    # Test datasets
    print("\n1. Testing Dataset Operations")
    print("-" * 40)
    all_results.update(test_datasets_operations())
    
    # Test examples
    print("\n2. Testing Example Operations")
    print("-" * 40)
    all_results.update(test_examples_operations())
    
    # Test annotation queues
    print("\n3. Testing Annotation Queue Operations")
    print("-" * 40)
    all_results.update(test_annotation_queues_operations())
    
    # Test advanced dataset operations
    print("\n4. Testing Advanced Dataset Operations")
    print("-" * 40)
    all_results.update(test_dataset_advanced_operations())
    
    # Save results
    output_path = os.path.join(os.path.dirname(__file__), "datasets_annotation_results.json")
    with open(output_path, "w") as f:
        json.dump(all_results, f, indent=2, default=str)
    
    print(f"\nTest results saved to: {output_path}")
    print("\nTesting completed!")
    
    # Print summary
    print("\nSummary:")
    print("-" * 20)
    for category, results in all_results.items():
        if isinstance(results, dict) and category != "timestamp" and category != "api_key_configured":
            success_count = sum(1 for k, v in results.items() 
                              if isinstance(v, dict) and v.get("success", False))
            total_count = len([k for k, v in results.items() 
                             if isinstance(v, dict) and "success" in v])
            print(f"{category.replace('_', ' ').title()}: {success_count}/{total_count} operations successful")


if __name__ == "__main__":
    main()
