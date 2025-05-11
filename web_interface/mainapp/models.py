from django.db import models
from django.contrib.auth.models import User


class Job(models.Model):
    job_id = models.AutoField(primary_key=True)  # 自动增长的作业号
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # 关联用户
    task_type = models.CharField(max_length=255)  # 任务类型
    status = models.CharField(max_length=50, default="Pending")  # 任务状态
    created_at = models.DateTimeField(auto_now_add=True)  # 任务创建时间

    def __str__(self):
        return f"Job {self.job_id} - {self.task_type} - {self.status}"


class UserRanking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task_type = models.CharField(max_length=255)
    best_score = models.FloatField(default=0.0)

    class Meta:
        unique_together = ('user', 'task_type')
