一个基于Django制作的helixer封装, 简单的说就是给Helixer命令行搞了一个投递任务的网页, 目前非常简陋


任务调用的命令见 `/tasks/views.py`, 按照自己实际情况更改

```python

    docker_command = [
        "docker", "run", "--runtime=nvidia", "--rm", "--name", "helixer_testing_v0.3.2_cuda_11.2.0-cudnn8",
        "--mount", f"type=bind,source={os.getcwd()}/media,target=/home/helixer_user/shared",
        "--mount", f"type=bind,source={os.getcwd()}/Helixer,target=/home/helixer_user/.local/share/Helixer",
        "gglyptodon/helixer-docker:helixer_v0.3.2_cuda_11.8.0-cudnn8",
        "sh", "-c",
        # f"sleep 5 && touch /home/helixer_user/shared/gff_files/{gff_filename}"
        f"Helixer.py --fasta-path /home/helixer_user/shared/uploads/{fasta_file_name} --lineage {lineage} --gff-output-path /home/helixer_user/shared/gff_files/{gff_filename} --batch-size 32 --species {gff_label}"
    ]

```

启动方法如下

第一步，安装django

```bash
pip install django
```

第二步:  初始化数据库 （在helixer_task_manager 目录下）

```
python manage.py migrate
python manage.py createsuperuser
```

第三步: 运行服务 (在helixer_task_manager 目录下)

```bash
python manage.py runserver
```