import torch

random1 = torch.rand(7, 7)
random2 = torch.rand(1, 7)

result = torch.mathmul(random2, random1.T)
print(result)

random3 = torch.rand(1,1,1,10)

random3 = random3.view(-1)
print(random3.shape)