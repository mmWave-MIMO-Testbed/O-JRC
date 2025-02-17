import torch
import numpy as np

print(torch.__version__)
print(torch.cuda.is_available())

##################
#Build the CNN for CSI
#Radar CSI with size: 64*8. 64 subcarrier, and 8 TX-RX pairs
#Radar CSI: convert to phase and maginitude 
###################
###  CSI 为 64*8 大小

import torch
import torch.nn as nn
import torch.nn.functional as F

class CSIClassifier(nn.Module):
    def __init__(self):
        super(CSIClassifier, self).__init__()
        # 输入通道为2，即相位和幅度
        self.conv1 = nn.Conv2d(2, 16, (3, 5), padding=(1, 2))  # 考虑到高度较小，使用更大的宽度卷积核
        self.pool1 = nn.MaxPool2d((2, 1))  # 针对高度进行池化，不改变宽度
        self.conv2 = nn.Conv2d(16, 32, (3, 5), padding=(1, 2))
        self.pool2 = nn.MaxPool2d((2, 1))
        self.conv3 = nn.Conv2d(32, 64, (3, 5), padding=(1, 2))
        self.pool3 = nn.MaxPool2d((2, 1))
        
        # 计算池化后的尺寸，假设每次池化后高度减半
        # 假设经过三次池化，高度变为1，宽度保持64
        self.to_linear = 64 * 64  # 更新全连接层的输入尺寸
        self.fc1 = nn.Linear(self.to_linear, 128)
        self.fc2 = nn.Linear(128, 64)  # 输出层：64种标签

    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = self.pool1(x)
        x = F.relu(self.conv2(x))
        x = self.pool2(x)
        x = F.relu(self.conv3(x))
        x = self.pool3(x)
        x = x.view(-1, self.to_linear)  # 展平
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        return x

# 创建模型实例
model = CSIClassifier()

## Load Data

# import numpy as np
# import os
# import re

# def process_csv(full_filename):
#     # 使用 numpy.genfromtxt 读取数据，跳过标题行
#     data = np.genfromtxt(full_filename, delimiter=',', dtype=str, skip_header=1)
#     num_rows = data.shape[0]
#     complex_responses = np.zeros((num_rows, num_subcarriers, num_txrx), dtype=complex)

#     for i in range(num_rows):
#         data_row = data[i]
#         column_index = 0
#         for j in range(num_txrx):
#             for k in range(num_subcarriers):
#                 real_part_index = column_index
#                 imag_part_index = column_index + 1

#                 if imag_part_index >= data_row.size:
#                     print(f"Index out of range in file: {full_filename}, row: {i}, column: {imag_part_index}")
#                     continue  # 跳过当前循环

#                 # 使用正则表达式提取数字
#                 real_part_match = re.findall(r'[-\d\.]+', data_row[real_part_index])
#                 imag_part_match = re.findall(r'[-\d\.]+', data_row[imag_part_index])

#                 if real_part_match and imag_part_match:
#                     real_part = float(real_part_match[0])
#                     imag_part = float(imag_part_match[0])
#                 else:
#                     continue  # 如果匹配失败，跳过当前循环

#                 complex_responses[i, k, j] = complex(real_part, imag_part)
#                 column_index += 2

#     return complex_responses

# # 定义根目录和其他参数
# #root_dir = './experiment_1a_single_target/Metal_reflector/'
# #root_dir = './experiment_1a_single_target/Human/'
# root_dir = './experiment1_static'
# num_subcarriers = 64
# num_txrx = 8

# # 遍历location文件夹
# for location_id in range(1, 28):  # location1到location27
#     location_folder = f"location{location_id}"
#     location_path = os.path.join(root_dir, location_folder)

#     combined_responses = []  # 用于存储合并的数据

#     # 遍历test1和test2文件夹
#     for test_folder in ['test1', 'test2']:
#         csv_file_path = os.path.join(location_path, test_folder, 'radar_chan.csv')
#         if os.path.exists(csv_file_path):
#             complex_responses = process_csv(csv_file_path)
#             combined_responses.append(complex_responses)

#     # 如果有数据被处理，则合并并保存
#     if combined_responses:
#         combined_responses = np.concatenate(combined_responses, axis=0)  # 假设沿着第一个维度合并
#         save_npy_path = os.path.join(location_path, 'combined_complex_responses.npy')
#         np.save(save_npy_path, combined_responses)
#         print(f"Saved combined data to {save_npy_path}")

# 假设 'combined_complex_responses.npy' 是你保存的文件名
#file_path = './experiment_1a_single_target/Metal_reflector/location1/combined_complex_responses.npy'
#file_path = './experiment_1a_single_target/Human/location1/combined_complex_responses.npy'
file_path = './experiment1_static/location1/combined_complex_responses.npy'

# 使用 numpy.load() 加载.npy文件
data = np.load(file_path)

# # 打印加载的数据
# print("Loaded data:")
# print(data)

# 如果数据量非常大，考虑打印数据的一部分或其统计信息
print("\nData shape:", data.shape)
print("Data type:", data.dtype)
print("First element of data:", data[0])  # 打印第一个元素

import os
import torch
from torch.utils.data import Dataset
import numpy as np

class CSIDataset(Dataset):
    def __init__(self, root_dir, transform=None):
        """
        root_dir: 数据的根目录
        transform: 应用于数据的预处理函数
        """
        self.root_dir = root_dir
        self.transform = transform
        self.samples = []
        
        # 读取数据和标签
        for label in range(1, 28):  # 从location1到location27
            folder_name = f'location{label}'
            folder_path = os.path.join(root_dir, folder_name)
            filename = 'combined_complex_responses.npy'
            file_path = os.path.join(folder_path, filename)
            if os.path.exists(file_path):
                data = np.load(file_path)
                # 处理每一组数据
                for i in range(data.shape[0]):
                    single_sample = data[i]  # 单个样本数据
                    magnitude = np.abs(single_sample)
                    phase = np.angle(single_sample)
                    if self.transform:
                        magnitude, phase = self.transform(magnitude, phase)
                    sample = np.stack([magnitude, phase], axis=0)
                    self.samples.append((torch.tensor(sample, dtype=torch.float32), label - 1))

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
#         file_path, label = self.samples[idx]
#         # 加载数据
#         data = np.load(file_path)  # 假设数据存储为.npy文件
#         # 转换为相位和幅度
#         magnitude = np.abs(data)
#         phase = np.angle(data)
        
#         # 转换为Tensor
#         if self.transform:
#             magnitude, phase = self.transform(magnitude, phase)
        
#         # 堆叠相位和幅度形成两个通道
#         sample = np.stack([magnitude, phase], axis=0)
#         sample = torch.tensor(sample, dtype=torch.float32)
        
#         return sample, label
        return self.samples[idx]

# 可以添加转换函数，例如标准化等
def transform(magnitude, phase):
    # 归一化处理 if needed
    magnitude = (magnitude - np.mean(magnitude)) / np.std(magnitude)
    phase = (phase - np.mean(phase)) / np.std(phase)
    return magnitude, phase

from torch.utils.data import DataLoader
from torch.utils.data import random_split

# 创建数据集实例
#dataset = CSIDataset(root_dir = './experiment_1a_single_target/Metal_reflector/', transform=transform)
#dataset = CSIDataset(root_dir = './experiment_1a_single_target/Human/', transform=transform)
dataset = CSIDataset(root_dir = './experiment1_static', transform=transform)

# 创建了一个名为dataset的CSIDataset实例
total_samples = len(dataset)
print(f'dataset length: {total_samples}')
train_size = int(total_samples * 0.9)
print(f'training length: {train_size}')
validation_size = total_samples - train_size
print(f'validation length: {validation_size}')

# 随机分割数据集
train_dataset, validation_dataset = random_split(dataset, [train_size, validation_size])

# 创建对应的DataLoader
train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True, num_workers=8, pin_memory=True)
validation_loader = DataLoader(validation_dataset, batch_size=32, shuffle=False, num_workers=8, pin_memory=True)
from torch import nn, optim

# def train_and_validate(model, train_loader, validation_loader, num_epochs):
#     model = model.to('cuda')
#     criterion = nn.CrossEntropyLoss()
#     optimizer = optim.Adam(model.parameters(), lr=0.001)

#     for epoch in range(num_epochs):
#         # 训练阶段
#         model.train()
#         all_inputs, all_labels = [], []
#         for inputs, labels in train_loader:
#             inputs, labels = inputs.to('cuda'), labels.to('cuda')
#             all_inputs.append(inputs)
#             all_labels.append(labels)
            
#         # 合并整个epoch的数据
#         combined_inputs = torch.cat(all_inputs, dim=0)
#         combined_labels = torch.cat(all_labels, dim=0)
            
#         # 使用合并后的数据进行训练
#         optimizer.zero_grad()
#         outputs = model(combined_inputs)
#         loss = criterion(outputs, combined_labels)
#         loss.backward()
#         optimizer.step()

#         # 验证阶段
#         model.eval()
#         eval_inputs, eval_labels = [], []
#         with torch.no_grad():
#             total = 0
#             correct = 0
#             for inputs, labels in validation_loader:
#                 inputs, labels = inputs.to('cuda'), labels.to('cuda')
#                 #eval_inputs.append(inputs)
#                 #eval_labels.append(labels)
                
#             # 合并整个epoch的数据
#             #eval_combined_inputs = torch.cat(eval_inputs, dim=0)
#             #eval_combined_labels = torch.cat(eval_labels, dim=0)
                
#             #outputs = model(eval_combined_inputs)
#             #_, predicted = torch.max(outputs.data, 1)
#             #total += labels.size(0)
#             #correct += (predicted == labels).sum().item()
#                 outputs = model(inputs)
#                 _, predicted = torch.max(outputs.data, 1)
#                 total += labels.size(0)
#                 correct += (predicted == labels).sum().item()

#         validation_accuracy = 100 * correct / total
#         print(f'Epoch [{epoch+1}/{num_epochs}], Loss: {loss.item():.4f}, Validation Accuracy: {validation_accuracy:.2f}%')

# # 调用函数训练和验证模型
# num_epochs = 50
# model = CSIClassifier()
# train_and_validate(model, train_loader, validation_loader, num_epochs)

# 验证每一个class下的准确率

from torch import nn, optim
import torch

def train_and_validate(model, train_loader, validation_loader, num_epochs):
    model = model.to('cpu')
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    for epoch in range(num_epochs):
        # 训练阶段
        model.train()
        all_inputs, all_labels = [], []
        for inputs, labels in train_loader:
            inputs, labels = inputs.to('cpu'), labels.to('cpu')
            all_inputs.append(inputs)
            all_labels.append(labels)
        
        # 合并整个epoch的数据
        combined_inputs = torch.cat(all_inputs, dim=0)
        combined_labels = torch.cat(all_labels, dim=0)
        
        # 使用合并后的数据进行训练
        optimizer.zero_grad()
        outputs = model(combined_inputs)
        loss = criterion(outputs, combined_labels)
        loss.backward()
        optimizer.step()

        # 验证阶段
        model.eval()
        correct = 0
        total = 0

        # 获取类别数
        num_classes = 27 # number of labels
        correct_per_class = torch.zeros(num_classes).to('cpu')
        total_per_class = torch.zeros(num_classes).to('cpu')

        with torch.no_grad():
            for inputs, labels in validation_loader:
                inputs, labels = inputs.to('cpu'), labels.to('cpu')
                outputs = model(inputs)
                _, predicted = torch.max(outputs.data, 1)

                total += labels.size(0)
                correct += (predicted == labels).sum().item()

                # 更新每个类别的正确预测和总数
                for i in range(len(labels)):
                    label = labels[i]
                    pred = predicted[i]
                    total_per_class[label] += 1
                    if pred == label:
                        correct_per_class[label] += 1

        validation_accuracy = 100 * correct / total
        print(f'Epoch [{epoch+1}/{num_epochs}], Loss: {loss.item():.4f}, Validation Accuracy: {validation_accuracy:.2f}%')

        # 输出每个类别的准确率
        for class_idx in range(num_classes):
            if total_per_class[class_idx] > 0:  # 确保该类别有样本
                class_accuracy = 100 * correct_per_class[class_idx] / total_per_class[class_idx]
                print(f'Class {class_idx} Accuracy: {class_accuracy:.2f}%')

# 调用函数训练和验证模型
num_epochs = 50
model = CSIClassifier()
train_and_validate(model, train_loader, validation_loader, num_epochs)
torch.save(model.state_dict(), 'OJRC_CNN_trained_model.pth')
print('model saved')
