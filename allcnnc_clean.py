import torch
import torch.nn as nn
import functools
class AllCNNC(nn.Module):
    def __init__(self, use_bias = False):
        super(AllCNNC, self).__init__()
        p_init = 0.2
        p = 0.5
        stride = 1
        padding = 1
        kernel_size = 3
        N_channels = 96 
        N_channels_2 = N_channels * 2
        eps = 2e-5
        self.really_equivariant = True  
        if self.really_equivariant:
            self.pooling = torch.max_pool2d
        self.c1 = nn.Conv2d(in_channels=3           , out_channels=N_channels  , kernel_size=kernel_size, stride=stride, padding=padding, bias=use_bias)
        self.c2 = nn.Conv2d(in_channels=N_channels  , out_channels=N_channels  , kernel_size=kernel_size, stride=stride, padding=padding, bias=use_bias)
        self.c3 = nn.Conv2d(in_channels=N_channels  , out_channels=N_channels  , kernel_size=kernel_size, stride=2     , padding=padding, bias=use_bias)
        if self.really_equivariant:
            self.c3 = nn.Conv2d(in_channels=N_channels, out_channels=N_channels, kernel_size=kernel_size, stride=stride, padding=padding, bias=use_bias)
        self.c4 = nn.Conv2d(in_channels=N_channels  , out_channels=N_channels_2, kernel_size=kernel_size, stride=stride, padding=padding, bias=use_bias)
        self.c5 = nn.Conv2d(in_channels=N_channels_2, out_channels=N_channels_2, kernel_size=kernel_size, stride=stride, padding=padding, bias=use_bias)
        self.c6 = nn.Conv2d(in_channels=N_channels_2, out_channels=N_channels_2, kernel_size=kernel_size, stride=2     , padding=padding, bias=use_bias)
        if self.really_equivariant:
            self.c6 = nn.Conv2d(in_channels=N_channels_2, out_channels=N_channels_2, kernel_size=kernel_size, stride=stride, padding=padding, bias=use_bias)
        self.c7 = nn.Conv2d(in_channels=N_channels_2, out_channels=N_channels_2, kernel_size=kernel_size, stride=stride, padding=padding, bias=use_bias)
        self.c8 = nn.Conv2d(in_channels=N_channels_2, out_channels=N_channels_2, kernel_size=1          , stride=stride, padding=0      , bias=use_bias)
        self.c9 = nn.Conv2d(in_channels=N_channels_2, out_channels=10          , kernel_size=1          , stride=stride, padding=0      , bias=use_bias)
        self.dp_init = nn.Dropout(p_init)
        self.dp = nn.Dropout(p)
        self.bn1 = nn.BatchNorm2d(num_features=N_channels  , eps=eps)
        self.bn2 = nn.BatchNorm2d(num_features=N_channels  , eps=eps)
        self.bn3 = nn.BatchNorm2d(num_features=N_channels  , eps=eps)
        self.bn4 = nn.BatchNorm2d(num_features=N_channels_2, eps=eps)
        self.bn5 = nn.BatchNorm2d(num_features=N_channels_2, eps=eps)
        self.bn6 = nn.BatchNorm2d(num_features=N_channels_2, eps=eps)
        self.bn7 = nn.BatchNorm2d(num_features=N_channels_2, eps=eps)
        self.bn8 = nn.BatchNorm2d(num_features=N_channels_2, eps=eps)
        self.bn9 = nn.BatchNorm2d(num_features=10          , eps=eps)
        wtscale = 0.05 
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                m.weight.data.normal_(0, wtscale)
                if use_bias: m.bias.data.fill_(0.0)
    def forward(self, x):
        out = torch.relu(self.bn1(self.c1(self.dp_init(x))))
        out = torch.relu(self.bn2(self.c2(out)))
        if self.really_equivariant:
            out = self.c3(out)
            out = self.pooling(out, kernel_size=2, stride=2, padding=0)
            out = self.dp(torch.relu(self.bn3(out)))
        else:
            out = self.dp(torch.relu(self.bn3(self.c3(out))))
        out = torch.relu(self.bn4(self.c4(out)))
        out = torch.relu(self.bn5(self.c5(out)))
        if self.really_equivariant:
            out = self.c6(out)
            out = self.pooling(out, kernel_size=2, stride=2, padding=0)
            out = self.dp(torch.relu(self.bn6(out)))
        else:
            out = self.dp(torch.relu(self.bn6(self.c6(out))))
        out = torch.relu(self.bn7(self.c7(out)))
        out = torch.relu(self.bn8(self.c8(out)))
        out = torch.relu(self.bn9(self.c9(out)))
        out = torch.nn.functional.avg_pool2d(out, out.size()[3]).squeeze()
        return out
class P4AllCNNC(nn.Module):
    def __init__(self, use_bias=False):
        super(P4AllCNNC, self).__init__()
        import importlib
        group_name = 'SE2'
        group = importlib.import_module('attgconv.group.' + group_name)
        import attgconv
        se2_layers = attgconv.layers(group)  
        self.h_grid = se2_layers.H.grid_global(4)
        p_init = 0.2
        p = 0.5
        stride = 1
        padding = 1
        kernel_size = 3
        N_channels = 48 
        N_channels_2 = N_channels * 2
        eps = 2e-5
        wscale = 0.035  
        self.really_equivariant = True   
        if self.really_equivariant:
            self.pooling = se2_layers.max_pooling_Rn
        self.c1 = se2_layers.ConvRnG(N_in=3          , N_out=N_channels  , kernel_size=kernel_size, h_grid=self.h_grid,                           stride=stride, padding=padding, wscale=wscale)
        self.c2 = se2_layers.ConvGG(N_in=N_channels  , N_out=N_channels  , kernel_size=kernel_size, h_grid=self.h_grid, input_h_grid=self.h_grid, stride=stride, padding=padding, wscale=wscale)
        self.c3 = se2_layers.ConvGG(N_in=N_channels  , N_out=N_channels  , kernel_size=kernel_size, h_grid=self.h_grid, input_h_grid=self.h_grid, stride=2     , padding=padding, wscale=wscale)
        if self.really_equivariant:
            self.c3 = se2_layers.ConvGG(N_in=N_channels, N_out=N_channels, kernel_size=kernel_size, h_grid=self.h_grid, input_h_grid=self.h_grid, stride=stride, padding=padding, wscale=wscale)
        self.c4 = se2_layers.ConvGG(N_in=N_channels  , N_out=N_channels_2, kernel_size=kernel_size, h_grid=self.h_grid, input_h_grid=self.h_grid, stride=stride, padding=padding, wscale=wscale)
        self.c5 = se2_layers.ConvGG(N_in=N_channels_2, N_out=N_channels_2, kernel_size=kernel_size, h_grid=self.h_grid, input_h_grid=self.h_grid, stride=stride, padding=padding, wscale=wscale)
        self.c6 = se2_layers.ConvGG(N_in=N_channels_2, N_out=N_channels_2, kernel_size=kernel_size, h_grid=self.h_grid, input_h_grid=self.h_grid, stride=2     , padding=padding, wscale=wscale)
        if self.really_equivariant:
            self.c6 = se2_layers.ConvGG(N_in=N_channels_2, N_out=N_channels_2, kernel_size=kernel_size, h_grid=self.h_grid, input_h_grid=self.h_grid, stride=stride, padding=padding,  wscale=wscale)
        self.c7 = se2_layers.ConvGG(N_in=N_channels_2, N_out=N_channels_2, kernel_size=kernel_size, h_grid=self.h_grid, input_h_grid=self.h_grid, stride=stride, padding=padding, wscale=wscale)
        self.c8 = se2_layers.ConvGG(N_in=N_channels_2, N_out=N_channels_2, kernel_size=1          , h_grid=self.h_grid, input_h_grid=self.h_grid, stride=stride, padding=0      , wscale=wscale)
        self.c9 = se2_layers.ConvGG(N_in=N_channels_2, N_out=10          , kernel_size=1          , h_grid=self.h_grid, input_h_grid=self.h_grid, stride=stride, padding=0      , wscale=wscale)
        self.dp_init = nn.Dropout(p_init)
        self.dp = nn.Dropout(p)
        self.bn1 = nn.BatchNorm3d(num_features=N_channels  , eps=eps)
        self.bn2 = nn.BatchNorm3d(num_features=N_channels  , eps=eps)
        self.bn3 = nn.BatchNorm3d(num_features=N_channels  , eps=eps)
        self.bn4 = nn.BatchNorm3d(num_features=N_channels_2, eps=eps)
        self.bn5 = nn.BatchNorm3d(num_features=N_channels_2, eps=eps)
        self.bn6 = nn.BatchNorm3d(num_features=N_channels_2, eps=eps)
        self.bn7 = nn.BatchNorm3d(num_features=N_channels_2, eps=eps)
        self.bn8 = nn.BatchNorm3d(num_features=N_channels_2, eps=eps)
        self.bn9 = nn.BatchNorm3d(num_features=10, eps=eps)
    def forward(self, x):
        out = torch.relu(self.bn1(self.c1(self.dp_init(x))))
        out = torch.relu(self.bn2(self.c2(out)))
        if self.really_equivariant:
            out = self.c3(out)
            out = self.pooling(out, kernel_size=2, stride=2, padding=0)
            out = self.dp(torch.relu(self.bn3(out)))
        else:
            out = self.dp(torch.relu(self.bn3(self.c3(out))))
        out = torch.relu(self.bn4(self.c4(out)))
        out = torch.relu(self.bn5(self.c5(out)))
        if self.really_equivariant:
            out = self.c6(out)
            out = self.pooling(out, kernel_size=2, stride=2, padding=0)
            out = self.dp(torch.relu(self.bn6(out)))
        else:
            out = self.dp(torch.relu(self.bn6(self.c6(out))))
        out = torch.relu(self.bn7(self.c7(out)))
        out = torch.relu(self.bn8(self.c8(out)))
        out = torch.relu(self.bn9(self.c9(out)))
        out = torch.nn.functional.avg_pool3d(out, out.size()[2:]).squeeze()
        if False:
            from attgconv.attention_layers import fSpatialAttentionGG
            from attgconv.attention_layers import fSpatialAttention
            import numpy as np
            import matplotlib.pyplot as plt
            inx = 0
            B = 60
            maps = []
            for m in self.modules():
                if isinstance(m, fSpatialAttention):
                    map = m.att_map.cpu().detach()
                    inx = map.shape[-2]
            upsample = torch.nn.UpsamplingBilinear2d(size=inx)
            for m in self.modules():
                if isinstance(m, fSpatialAttentionGG):
                    map = m.att_map.cpu().detach()
                    map = map.reshape(map.shape[0], 4, map.shape[-2], map.shape[-1])
                    map = upsample(map)
                    map = map.reshape(map.shape[0], 1, 4, map.shape[-2], map.shape[-1])
                    maps.append(map)
            map_0 = maps[0]
            for i in range(len(maps) - 1):
                map_0 = map_0 * maps[i + 1]
            plt.figure()
            plt.imshow(map_0.sum(-3)[B, 0])
            plt.show()
            cmap = plt.cm.jet
            time_samples = 4
            scale = 10
            z = np.zeros([inx, inx])
            plt.figure(dpi=600)
            for t in range(4):
                plt.imshow(map_0.sum(-3)[B, 0])
                if t == 0:
                    plt.quiver(z, map_0[B, 0, t, :, :], color='red', label=r'$0^{\circ}$', scale=scale)
                if t == 2:
                    plt.quiver(z, -map_0[B, 0, t, :, :], color=cmap(t / time_samples), label=r'$180^{\circ}$', scale=scale)
                if t == 1:
                    plt.quiver(-map_0[B, 0, t, :, :], z, color='cyan', label=r'$90^{\circ}$', scale=scale)
                if t == 3:
                    plt.quiver(map_0[B, 0, t, :, :], z, color=cmap(t / time_samples), label=r'$270^{\circ}$',  scale=scale)
            plt.legend(loc='upper right')
            plt.axis('off')
            plt.tight_layout()
            plt.show()
        return out
class fA_P4AllCNNC(P4AllCNNC):
    def __init__(self):
        super(fA_P4AllCNNC, self).__init__()
        import importlib
        group_name = 'SE2'
        group = importlib.import_module('attgconv.group.' + group_name)
        import attgconv
        se2_layers = attgconv.layers(group)  
        n_grid = 4
        h_grid = se2_layers.H.grid_global(n_grid)
        p_init = 0.2
        p = 0.5
        stride = 1
        padding = 1
        kernel_size = 3
        N_channels = 48 
        N_channels_2 = N_channels * 2
        eps = 2e-5
        wscale = 0.035  
        ch_ratio = 16
        sp_kernel_size = 7
        sp_padding = (sp_kernel_size // 2)
        self.group_name = group_name
        self.group = group
        self.layers = se2_layers
        self.n_grid = n_grid
        self.h_grid = h_grid
        self.p = p
        self.stride = stride
        self.padding = padding
        self.kernel_size = kernel_size
        self.N_channels = N_channels
        self.eps = eps
        self.ch_ratio = ch_ratio
        self.sp_kernel_size = sp_kernel_size
        self.sp_dilation = sp_padding
        from attgconv.attention_layers import fChannelAttention as ch_RnG
        from attgconv.attention_layers import fChannelAttentionGG 
        from attgconv.attention_layers import fSpatialAttention 
        from attgconv.attention_layers import fSpatialAttentionGG
        ch_GG = functools.partial(fChannelAttentionGG, N_h_in=n_grid)
        sp_RnG = functools.partial(fSpatialAttention, wscale=wscale)
        sp_GG = functools.partial(fSpatialAttentionGG, group=group, input_h_grid=self.h_grid, wscale=wscale)
        self.c1 = se2_layers.fAttConvRnG(N_in=3          , N_out=N_channels  , kernel_size=kernel_size, h_grid=self.h_grid, stride=stride, padding=padding, wscale=wscale,
                                        channel_attention=ch_RnG(N_in=3        , ratio=1),
                                        spatial_attention=sp_RnG(group=group, kernel_size=sp_kernel_size, h_grid=self.h_grid)
                                        )
        self.c2 = se2_layers.fAttConvGG(N_in=N_channels  , N_out=N_channels  , kernel_size=kernel_size, h_grid=self.h_grid, input_h_grid=self.h_grid, stride=stride, padding=padding, wscale=wscale,
                                       channel_attention=ch_GG(N_in=N_channels  , ratio=ch_ratio),
                                       spatial_attention=sp_GG(kernel_size=sp_kernel_size)
                                       )
        self.c3 = se2_layers.fAttConvGG(N_in=N_channels  , N_out=N_channels  , kernel_size=kernel_size, h_grid=self.h_grid, input_h_grid=self.h_grid, stride=2     , padding=padding, wscale=wscale,
                                       channel_attention=ch_GG(N_in=N_channels  , ratio=ch_ratio),
                                       spatial_attention=sp_GG(kernel_size=sp_kernel_size)
                                       )
        if self.really_equivariant:
            self.c3 = se2_layers.fAttConvGG(N_in=N_channels, N_out=N_channels, kernel_size=kernel_size, h_grid=self.h_grid, input_h_grid=self.h_grid, stride=stride, padding=padding, wscale=wscale,
                                            channel_attention=ch_GG(N_in=N_channels, ratio=ch_ratio),
                                            spatial_attention=sp_GG(kernel_size=sp_kernel_size)
                                            )
        self.c4 = se2_layers.fAttConvGG(N_in=N_channels  , N_out=N_channels_2, kernel_size=kernel_size, h_grid=self.h_grid, input_h_grid=self.h_grid, stride=stride, padding=padding, wscale=wscale,
                                       channel_attention=ch_GG(N_in=N_channels  , ratio=ch_ratio),
                                       spatial_attention=sp_GG(kernel_size=sp_kernel_size)
                                       )
        self.c5 = se2_layers.fAttConvGG(N_in=N_channels_2, N_out=N_channels_2, kernel_size=kernel_size, h_grid=self.h_grid, input_h_grid=self.h_grid, stride=stride, padding=padding, wscale=wscale,
                                       channel_attention=ch_GG(N_in=N_channels_2, ratio=ch_ratio),
                                       spatial_attention=sp_GG(kernel_size=sp_kernel_size)
                                       )
        self.c6 = se2_layers.fAttConvGG(N_in=N_channels_2, N_out=N_channels_2, kernel_size=kernel_size, h_grid=self.h_grid, input_h_grid=self.h_grid, stride=2     , padding=padding, wscale=wscale,
                                       channel_attention=ch_GG(N_in=N_channels_2, ratio=ch_ratio),
                                       spatial_attention=sp_GG(kernel_size=sp_kernel_size)
                                       )
        if self.really_equivariant:
            self.c6 = se2_layers.fAttConvGG(N_in=N_channels_2, N_out=N_channels_2, kernel_size=kernel_size, h_grid=self.h_grid, input_h_grid=self.h_grid, stride=stride, padding=padding, wscale=wscale,
                                            channel_attention=ch_GG(N_in=N_channels_2, ratio=ch_ratio),
                                            spatial_attention=sp_GG(kernel_size=sp_kernel_size)
                                            )
        self.c7 = se2_layers.fAttConvGG(N_in=N_channels_2, N_out=N_channels_2, kernel_size=kernel_size, h_grid=self.h_grid, input_h_grid=self.h_grid, stride=stride, padding=padding, wscale=wscale,
                                       channel_attention=ch_GG(N_in=N_channels_2, ratio=ch_ratio),
                                       spatial_attention=sp_GG(kernel_size=sp_kernel_size)
                                       )
        self.c8 = se2_layers.fAttConvGG(N_in=N_channels_2, N_out=N_channels_2, kernel_size=1          , h_grid=self.h_grid, input_h_grid=self.h_grid, stride=stride, padding=0      , wscale=wscale,
                                       channel_attention=ch_GG(N_in=N_channels_2, ratio=ch_ratio),
                                       spatial_attention=sp_GG(kernel_size=sp_kernel_size)
                                       )
        self.c9 = se2_layers.fAttConvGG(N_in=N_channels_2, N_out=10          , kernel_size=1          , h_grid=self.h_grid, input_h_grid=self.h_grid, stride=stride, padding=0      , wscale=wscale,
                                       channel_attention=ch_GG(N_in=N_channels_2, ratio=ch_ratio),
                                       spatial_attention=sp_GG(kernel_size=sp_kernel_size)
                                       )
        self.dp_init = nn.Dropout(p_init)
        self.dp = nn.Dropout(p)
        self.bn1 = nn.BatchNorm3d(num_features=N_channels  , eps=eps)
        self.bn2 = nn.BatchNorm3d(num_features=N_channels  , eps=eps)
        self.bn3 = nn.BatchNorm3d(num_features=N_channels  , eps=eps)
        self.bn4 = nn.BatchNorm3d(num_features=N_channels_2, eps=eps)
        self.bn5 = nn.BatchNorm3d(num_features=N_channels_2, eps=eps)
        self.bn6 = nn.BatchNorm3d(num_features=N_channels_2, eps=eps)
        self.bn7 = nn.BatchNorm3d(num_features=N_channels_2, eps=eps)
        self.bn8 = nn.BatchNorm3d(num_features=N_channels_2, eps=eps)
        self.bn9 = nn.BatchNorm3d(num_features=10, eps=eps)
class P4MAllCNNC(nn.Module):
    def __init__(self):
        super(P4MAllCNNC, self).__init__()
        import importlib
        group_name = 'E2'
        group = importlib.import_module('attgconv.group.' + group_name)
        import attgconv
        e2_layers = attgconv.layers(group)  
        self.h_grid = e2_layers.H.grid_global(8) 
        p_init = 0.2
        p = 0.5
        stride = 1
        padding = 1
        kernel_size = 3
        N_channels = 32 
        N_channels_2 = N_channels * 2
        eps = 2e-5
        wscale = 0.035  
        self.really_equivariant = True  
        if self.really_equivariant:
            self.pooling = e2_layers.max_pooling_Rn
        self.c1 = e2_layers.ConvRnG(N_in=3          , N_out=N_channels  , kernel_size=kernel_size, h_grid=self.h_grid, stride=stride, padding=padding, wscale=wscale)
        self.c2 = e2_layers.ConvGG(N_in=N_channels  , N_out=N_channels  , kernel_size=kernel_size, h_grid=self.h_grid, input_h_grid=self.h_grid, stride=stride, padding=padding, wscale=wscale)
        self.c3 = e2_layers.ConvGG(N_in=N_channels  , N_out=N_channels  , kernel_size=kernel_size, h_grid=self.h_grid, input_h_grid=self.h_grid, stride=2     , padding=padding, wscale=wscale)
        if self.really_equivariant:
            self.c3 = e2_layers.ConvGG(N_in=N_channels, N_out=N_channels, kernel_size=kernel_size, h_grid=self.h_grid, input_h_grid=self.h_grid, stride=stride, padding=padding, wscale=wscale)
        self.c4 = e2_layers.ConvGG(N_in=N_channels  , N_out=N_channels_2, kernel_size=kernel_size, h_grid=self.h_grid, input_h_grid=self.h_grid, stride=stride, padding=padding, wscale=wscale)
        self.c5 = e2_layers.ConvGG(N_in=N_channels_2, N_out=N_channels_2, kernel_size=kernel_size, h_grid=self.h_grid, input_h_grid=self.h_grid, stride=stride, padding=padding, wscale=wscale)
        self.c6 = e2_layers.ConvGG(N_in=N_channels_2, N_out=N_channels_2, kernel_size=kernel_size, h_grid=self.h_grid, input_h_grid=self.h_grid, stride=2     , padding=padding, wscale=wscale)
        if self.really_equivariant:
            self.c6 = e2_layers.ConvGG(N_in=N_channels_2, N_out=N_channels_2, kernel_size=kernel_size, h_grid=self.h_grid, input_h_grid=self.h_grid, stride=stride, padding=padding,  wscale=wscale)
        self.c7 = e2_layers.ConvGG(N_in=N_channels_2, N_out=N_channels_2, kernel_size=kernel_size, h_grid=self.h_grid, input_h_grid=self.h_grid, stride=stride, padding=padding, wscale=wscale)
        self.c8 = e2_layers.ConvGG(N_in=N_channels_2, N_out=N_channels_2, kernel_size=1          , h_grid=self.h_grid, input_h_grid=self.h_grid, stride=stride, padding=0      , wscale=wscale)
        self.c9 = e2_layers.ConvGG(N_in=N_channels_2, N_out=10          , kernel_size=1          , h_grid=self.h_grid, input_h_grid=self.h_grid, stride=stride, padding=0      , wscale=wscale)
        self.dp_init = nn.Dropout(p_init)
        self.dp = nn.Dropout(p)
        self.bn1 = nn.BatchNorm3d(num_features=N_channels  , eps=eps)
        self.bn2 = nn.BatchNorm3d(num_features=N_channels  , eps=eps)
        self.bn3 = nn.BatchNorm3d(num_features=N_channels  , eps=eps)
        self.bn4 = nn.BatchNorm3d(num_features=N_channels_2, eps=eps)
        self.bn5 = nn.BatchNorm3d(num_features=N_channels_2, eps=eps)
        self.bn6 = nn.BatchNorm3d(num_features=N_channels_2, eps=eps)
        self.bn7 = nn.BatchNorm3d(num_features=N_channels_2, eps=eps)
        self.bn8 = nn.BatchNorm3d(num_features=N_channels_2, eps=eps)
        self.bn9 = nn.BatchNorm3d(num_features=10, eps=eps)
    def forward(self, x):
        out = torch.relu(self.bn1(self.c1(self.dp_init(x))))
        out = torch.relu(self.bn2(self.c2(out)))
        if self.really_equivariant:
            out = self.c3(out)
            out = self.pooling(out, kernel_size=2, stride=2, padding=0)
            out = self.dp(torch.relu(self.bn3(out)))
        else:
            out = self.dp(torch.relu(self.bn3(self.c3(out))))
        out = torch.relu(self.bn4(self.c4(out)))
        out = torch.relu(self.bn5(self.c5(out)))
        if self.really_equivariant:
            out = self.c6(out)
            out = self.pooling(out, kernel_size=2, stride=2, padding=0)
            out = self.dp(torch.relu(self.bn6(out)))
        else:
            out = self.dp(torch.relu(self.bn6(self.c6(out))))
        out = torch.relu(self.bn7(self.c7(out)))
        out = torch.relu(self.bn8(self.c8(out)))
        out = torch.relu(self.bn9(self.c9(out)))
        out = torch.nn.functional.avg_pool3d(out, out.size()[2:]).squeeze()
        if False:
            from attgconv.attention_layers import fSpatialAttentionGG
            from attgconv.attention_layers import fSpatialAttention
            import numpy as np
            import matplotlib.pyplot as plt
            inx = 0
            B = 15
            maps = []
            for m in self.modules():
                if isinstance(m, fSpatialAttention):
                    map = m.att_map.cpu().detach()
                    inx = map.shape[-2]
                    map = map.expand(map.shape[0], 8, map.shape[2], map.shape[3]).unsqueeze(1)
                    maps.append(map)
            upsample = torch.nn.UpsamplingBilinear2d(size=inx)
            for m in self.modules():
                if isinstance(m, fSpatialAttentionGG):
                    map = m.att_map.cpu().detach()
                    map = map.reshape(map.shape[0], 8, map.shape[-2], map.shape[-1])
                    map = upsample(map)
                    map = map.reshape(map.shape[0], 1, 8, map.shape[-2], map.shape[-1])
                    maps.append(map)
            map_0 = maps[0]
            for i in range(len(maps) - 1):
                map_0 = map_0 * maps[i + 1]
            plt.figure()
            plt.imshow(map_0.sum(-3)[B, 0])
            plt.show()
            cmap = plt.cm.jet
            time_samples = 4
            scale = 10
            z = np.zeros([inx, inx])
            plt.figure(dpi=600)
            for t in range(4):
                plt.imshow(map_0.sum(-3)[B, 0])
                if t == 0:
                    plt.quiver(z, map_0[B, 0, t, :, :], color='red', label=r'$(1, 0^{\circ})$', scale=scale)
                if t == 2:
                    plt.quiver(z, -map_0[B, 0, t, :, :], color=cmap(t / time_samples), label=r'$(1, 180^{\circ})$', scale=scale)
                if t == 1:
                    plt.quiver(-map_0[B, 0, t, :, :], z, color='cyan', label=r'$(1, 90^{\circ})$', scale=scale)
                if t == 3:
                    plt.quiver(map_0[B, 0, t, :, :], z, color=cmap(t / time_samples), label=r'$(1, 270^{\circ})$',  scale=scale)
            plt.legend(loc='upper right')
            plt.axis('off')
            plt.tight_layout()
            plt.show()
            cmap = plt.cm.jet
            time_samples = 4
            scale = 10
            z = np.zeros([inx, inx])
            plt.figure(dpi=600)
            for t in range(4, 8, 1):
                plt.imshow(map_0.sum(-3)[B, 0])
                if t == 0:
                    plt.quiver(z, map_0[B, 0, t, :, :], color=cmap(t / time_samples), label=r'$(-1, 0^{\circ})$', scale=scale)
                if t == 2:
                    plt.quiver(z, -map_0[B, 0, t, :, :], color=cmap(t / time_samples), label=r'$(-1, 180^{\circ})$', scale=scale)
                if t == 1:
                    plt.quiver(-map_0[B, 0, t, :, :], z, color=cmap(t / time_samples), label=r'$(-1, 90^{\circ})$', scale=scale)
                if t == 3:
                    plt.quiver(map_0[B, 0, t, :, :], z, color=cmap(t / time_samples), label=r'$(-1, 270^{\circ})$',  scale=scale)
            plt.legend(loc='upper right')
            plt.axis('off')
            plt.tight_layout()
            plt.show()
        return out
class fA_P4MAllCNNC(P4MAllCNNC):
    def __init__(self):
        super(fA_P4MAllCNNC, self).__init__()
        import importlib
        group_name = 'E2'
        group = importlib.import_module('attgconv.group.' + group_name)
        import attgconv
        e2_layers = attgconv.layers(group)  
        n_grid = 8
        h_grid = e2_layers.H.grid_global(n_grid)
        p_init = 0.2
        p = 0.5
        stride = 1
        padding = 1
        kernel_size = 3
        N_channels = 32 
        N_channels_2 = N_channels * 2
        eps = 2e-5
        wscale = 0.035  
        ch_ratio = 16
        sp_kernel_size = 7
        sp_padding = (sp_kernel_size // 2)
        self.group_name = group_name
        self.group = group
        self.layers = e2_layers
        self.n_grid = n_grid
        self.h_grid = h_grid
        self.p = p
        self.stride = stride
        self.padding = padding
        self.kernel_size = kernel_size
        self.N_channels = N_channels
        self.eps = eps
        self.ch_ratio = ch_ratio
        self.sp_kernel_size = sp_kernel_size
        self.sp_dilation = sp_padding
        from attgconv.attention_layers import fChannelAttention as ch_RnG
        from attgconv.attention_layers import fChannelAttentionGG 
        from attgconv.attention_layers import fSpatialAttention 
        from attgconv.attention_layers import fSpatialAttentionGG
        ch_GG = functools.partial(fChannelAttentionGG, N_h_in=n_grid, group=group_name)
        sp_RnG = functools.partial(fSpatialAttention, wscale=wscale)
        sp_GG = functools.partial(fSpatialAttentionGG, group=group, input_h_grid=self.h_grid, wscale=wscale)
        self.c1 = e2_layers.fAttConvRnG(N_in=3          , N_out=N_channels  , kernel_size=kernel_size, h_grid=self.h_grid, stride=stride, padding=padding, wscale=wscale,
                                        channel_attention=ch_RnG(N_in=3        , ratio=1),
                                        spatial_attention=sp_RnG(group=group, kernel_size=sp_kernel_size, h_grid=self.h_grid)
                                        )
        self.c2 = e2_layers.fAttConvGG(N_in=N_channels  , N_out=N_channels  , kernel_size=kernel_size, h_grid=self.h_grid, input_h_grid=self.h_grid, stride=stride, padding=padding, wscale=wscale,
                                       channel_attention=ch_GG(N_in=N_channels  , ratio=ch_ratio),
                                       spatial_attention=sp_GG(kernel_size=sp_kernel_size)
                                       )
        self.c3 = e2_layers.fAttConvGG(N_in=N_channels  , N_out=N_channels  , kernel_size=kernel_size, h_grid=self.h_grid, input_h_grid=self.h_grid, stride=2     , padding=padding, wscale=wscale,
                                       channel_attention=ch_GG(N_in=N_channels  , ratio=ch_ratio),
                                       spatial_attention=sp_GG(kernel_size=sp_kernel_size)
                                       )
        if self.really_equivariant:
            self.c3 = e2_layers.fAttConvGG(N_in=N_channels, N_out=N_channels, kernel_size=kernel_size, h_grid=self.h_grid, input_h_grid=self.h_grid, stride=stride, padding=padding, wscale=wscale,
                                           channel_attention=ch_GG(N_in=N_channels, ratio=ch_ratio),
                                           spatial_attention=sp_GG(kernel_size=sp_kernel_size)
                                           )
        self.c4 = e2_layers.fAttConvGG(N_in=N_channels  , N_out=N_channels_2, kernel_size=kernel_size, h_grid=self.h_grid, input_h_grid=self.h_grid, stride=stride, padding=padding, wscale=wscale,
                                       channel_attention=ch_GG(N_in=N_channels  , ratio=ch_ratio),
                                       spatial_attention=sp_GG(kernel_size=sp_kernel_size)
                                       )
        self.c5 = e2_layers.fAttConvGG(N_in=N_channels_2, N_out=N_channels_2, kernel_size=kernel_size, h_grid=self.h_grid, input_h_grid=self.h_grid, stride=stride, padding=padding, wscale=wscale,
                                       channel_attention=ch_GG(N_in=N_channels_2, ratio=ch_ratio),
                                       spatial_attention=sp_GG(kernel_size=sp_kernel_size)
                                       )
        self.c6 = e2_layers.fAttConvGG(N_in=N_channels_2, N_out=N_channels_2, kernel_size=kernel_size, h_grid=self.h_grid, input_h_grid=self.h_grid, stride=2     , padding=padding, wscale=wscale,
                                       channel_attention=ch_GG(N_in=N_channels_2, ratio=ch_ratio),
                                       spatial_attention=sp_GG(kernel_size=sp_kernel_size)
                                       )
        if self.really_equivariant:
            self.c6 = e2_layers.fAttConvGG(N_in=N_channels_2, N_out=N_channels_2, kernel_size=kernel_size, h_grid=self.h_grid, input_h_grid=self.h_grid, stride=stride, padding=padding, wscale=wscale,
                                           channel_attention=ch_GG(N_in=N_channels_2, ratio=ch_ratio),
                                           spatial_attention=sp_GG(kernel_size=sp_kernel_size)
                                           )
        self.c7 = e2_layers.fAttConvGG(N_in=N_channels_2, N_out=N_channels_2, kernel_size=kernel_size, h_grid=self.h_grid, input_h_grid=self.h_grid, stride=stride, padding=padding, wscale=wscale,
                                       channel_attention=ch_GG(N_in=N_channels_2, ratio=ch_ratio),
                                       spatial_attention=sp_GG(kernel_size=sp_kernel_size)
                                       )
        self.c8 = e2_layers.fAttConvGG(N_in=N_channels_2, N_out=N_channels_2, kernel_size=1          , h_grid=self.h_grid, input_h_grid=self.h_grid, stride=stride, padding=0      , wscale=wscale,
                                       channel_attention=ch_GG(N_in=N_channels_2, ratio=ch_ratio),
                                       spatial_attention=sp_GG(kernel_size=sp_kernel_size)
                                       )
        self.c9 = e2_layers.fAttConvGG(N_in=N_channels_2, N_out=10          , kernel_size=1          , h_grid=self.h_grid, input_h_grid=self.h_grid, stride=stride, padding=0      , wscale=wscale,
                                       channel_attention=ch_GG(N_in=N_channels_2, ratio=ch_ratio),
                                       spatial_attention=sp_GG(kernel_size=sp_kernel_size)
                                       )
        self.dp_init = nn.Dropout(p_init)
        self.dp = nn.Dropout(p)
        self.bn1 = nn.BatchNorm3d(num_features=N_channels  , eps=eps)
        self.bn2 = nn.BatchNorm3d(num_features=N_channels  , eps=eps)
        self.bn3 = nn.BatchNorm3d(num_features=N_channels  , eps=eps)
        self.bn4 = nn.BatchNorm3d(num_features=N_channels_2, eps=eps)
        self.bn5 = nn.BatchNorm3d(num_features=N_channels_2, eps=eps)
        self.bn6 = nn.BatchNorm3d(num_features=N_channels_2, eps=eps)
        self.bn7 = nn.BatchNorm3d(num_features=N_channels_2, eps=eps)
        self.bn8 = nn.BatchNorm3d(num_features=N_channels_2, eps=eps)
        self.bn9 = nn.BatchNorm3d(num_features=10, eps=eps)
class A_P4AllCNNC(P4AllCNNC):
    def __init__(self, use_bias=False, attention=False):
        super(P4AllCNNC, self).__init__()
        import importlib
        group_name = 'SE2'
        group = importlib.import_module('attgconv.group.' + group_name)
        import attgconv
        se2_layers = attgconv.layers(group)  
        n_grid = 4
        self.h_grid = se2_layers.H.grid_global(n_grid)
        p_init = 0.2
        p = 0.5
        stride = 1
        padding = 1
        kernel_size = 3
        N_channels = 48 
        N_channels_2 = N_channels * 2
        eps = 2e-5
        wscale = 0.035  
        ch_ratio = 16        
        sp_kernel_size = 7
        self.ch_ratio = ch_ratio
        self.sp_kernel_size = sp_kernel_size
        from attgconv.attention_layers import ChannelAttention as ch_RnG
        from attgconv.attention_layers import ChannelAttentionGG 
        from attgconv.attention_layers import SpatialAttention 
        from attgconv.attention_layers import SpatialAttentionGG
        ch_GG = functools.partial(ChannelAttentionGG, N_h=n_grid, N_h_in=n_grid)
        sp_RnG = functools.partial(SpatialAttention, group=group, h_grid=self.h_grid, stride=stride, wscale=wscale)
        sp_GG = functools.partial(SpatialAttentionGG, group=group, h_grid=self.h_grid, input_h_grid=self.h_grid, stride=stride, wscale=wscale)
        self.c1 = se2_layers.AttConvRnG(N_in=3          , N_out=N_channels  , kernel_size=kernel_size, h_grid=self.h_grid, stride=stride, padding=padding, wscale=wscale,
                                        channel_attention=ch_RnG(N_out=N_channels, N_in=3        , ratio=1),
                                        spatial_attention=sp_RnG(N_out=N_channels, N_in=3        , kernel_size=sp_kernel_size)
                                        )
        self.c2 = se2_layers.AttConvGG(N_in=N_channels  , N_out=N_channels  , kernel_size=kernel_size, h_grid=self.h_grid, input_h_grid=self.h_grid, stride=stride, padding=padding, wscale=wscale,
                                       channel_attention=ch_GG(N_out= N_channels  , N_in=N_channels  , ratio=ch_ratio),
                                       spatial_attention=sp_GG(N_out= N_channels  , N_in=N_channels  , kernel_size=sp_kernel_size)
                                       )
        self.c3 = se2_layers.AttConvGG(N_in=N_channels  , N_out=N_channels  , kernel_size=kernel_size, h_grid=self.h_grid, input_h_grid=self.h_grid, stride=2     , padding=padding, wscale=wscale,
                                       channel_attention=ch_GG(N_out=N_channels  , N_in=N_channels  , ratio=ch_ratio),
                                       spatial_attention=sp_GG(N_out=N_channels  , N_in=N_channels  , kernel_size=sp_kernel_size)
                                       )
        self.c4 = se2_layers.AttConvGG(N_in=N_channels  , N_out=N_channels_2, kernel_size=kernel_size, h_grid=self.h_grid, input_h_grid=self.h_grid, stride=stride, padding=padding, wscale=wscale,
                                       channel_attention=ch_GG(N_out=N_channels_2, N_in=N_channels  , ratio=ch_ratio),
                                       spatial_attention=sp_GG(N_out=N_channels_2, N_in=N_channels  , kernel_size=sp_kernel_size)
                                       )
        self.c5 = se2_layers.AttConvGG(N_in=N_channels_2, N_out=N_channels_2, kernel_size=kernel_size, h_grid=self.h_grid, input_h_grid=self.h_grid, stride=stride, padding=padding, wscale=wscale,
                                       channel_attention=ch_GG(N_out=N_channels_2, N_in=N_channels_2, ratio=ch_ratio),
                                       spatial_attention=sp_GG(N_out=N_channels_2, N_in=N_channels_2, kernel_size=sp_kernel_size)
                                       )
        self.c6 = se2_layers.AttConvGG(N_in=N_channels_2, N_out=N_channels_2, kernel_size=kernel_size, h_grid=self.h_grid, input_h_grid=self.h_grid, stride=2     , padding=padding, wscale=wscale,
                                       channel_attention=ch_GG(N_out=N_channels_2, N_in=N_channels_2, ratio=ch_ratio),
                                       spatial_attention=sp_GG(N_out=N_channels_2, N_in=N_channels_2, kernel_size=sp_kernel_size)
                                       )
        self.c7 = se2_layers.AttConvGG(N_in=N_channels_2, N_out=N_channels_2, kernel_size=kernel_size, h_grid=self.h_grid, input_h_grid=self.h_grid, stride=stride, padding=padding, wscale=wscale,
                                       channel_attention=ch_GG(N_out=N_channels_2, N_in=N_channels_2, ratio=ch_ratio),
                                       spatial_attention=sp_GG(N_out=N_channels_2, N_in=N_channels_2, kernel_size=sp_kernel_size)
                                       )
        self.c8 = se2_layers.AttConvGG(N_in=N_channels_2, N_out=N_channels_2, kernel_size=1          , h_grid=self.h_grid, input_h_grid=self.h_grid, stride=stride, padding=0      , wscale=wscale,
                                       channel_attention=ch_GG(N_out=N_channels_2, N_in=N_channels_2, ratio=ch_ratio),
                                       spatial_attention=sp_GG(N_out=N_channels_2, N_in=N_channels_2, kernel_size=sp_kernel_size)
                                       )
        self.c9 = se2_layers.AttConvGG(N_in=N_channels_2, N_out=10          , kernel_size=1          , h_grid=self.h_grid, input_h_grid=self.h_grid, stride=stride, padding=0      , wscale=wscale,
                                       channel_attention=ch_GG(N_out=10          , N_in=N_channels_2, ratio=ch_ratio),
                                       spatial_attention=sp_GG(N_out=10          , N_in=N_channels_2, kernel_size=sp_kernel_size)
                                       )
        self.dp_init = nn.Dropout(p_init)
        self.dp = nn.Dropout(p)
        self.bn1 = nn.BatchNorm3d(num_features=N_channels  , eps=eps)
        self.bn2 = nn.BatchNorm3d(num_features=N_channels  , eps=eps)
        self.bn3 = nn.BatchNorm3d(num_features=N_channels  , eps=eps)
        self.bn4 = nn.BatchNorm3d(num_features=N_channels_2, eps=eps)
        self.bn5 = nn.BatchNorm3d(num_features=N_channels_2, eps=eps)
        self.bn6 = nn.BatchNorm3d(num_features=N_channels_2, eps=eps)
        self.bn7 = nn.BatchNorm3d(num_features=N_channels_2, eps=eps)
        self.bn8 = nn.BatchNorm3d(num_features=N_channels_2, eps=eps)
        self.bn9 = nn.BatchNorm3d(num_features=10, eps=eps)
class A_Ch_P4AllCNNC(A_P4AllCNNC):
    def __init__(self, use_bias=False, attention=False):
        super(A_Ch_P4AllCNNC, self).__init__()
        import importlib
        group_name = 'SE2'
        group = importlib.import_module('attgconv.group.' + group_name)
        import attgconv
        se2_layers = attgconv.layers(group)  
        n_grid = 4
        self.h_grid = se2_layers.H.grid_global(n_grid)
        p_init = 0.2
        p = 0.5
        stride = 1
        padding = 1
        kernel_size = 3
        N_channels = 48 
        N_channels_2 = N_channels * 2
        eps = 2e-5
        wscale = 0.035  
        ch_ratio = 16        
        sp_kernel_size = 7
        self.ch_ratio = ch_ratio
        self.sp_kernel_size = sp_kernel_size
        from attgconv.attention_layers import ChannelAttention as ch_RnG
        from attgconv.attention_layers import ChannelAttentionGG 
        from attgconv.attention_layers import SpatialAttention 
        from attgconv.attention_layers import SpatialAttentionGG
        ch_GG = functools.partial(ChannelAttentionGG, N_h=n_grid, N_h_in=n_grid)
        sp_RnG = functools.partial(SpatialAttention, group=group, h_grid=self.h_grid, stride=stride, wscale=wscale)
        sp_GG = functools.partial(SpatialAttentionGG, group=group, h_grid=self.h_grid, input_h_grid=self.h_grid, stride=stride, wscale=wscale)
        self.c1 = se2_layers.AttConvRnG(N_in=3          , N_out=N_channels  , kernel_size=kernel_size, h_grid=self.h_grid, stride=stride, padding=padding, wscale=wscale,
                                        channel_attention=ch_RnG(N_out=N_channels, N_in=3        , ratio=1),
                                        )
        self.c2 = se2_layers.AttConvGG(N_in=N_channels  , N_out=N_channels  , kernel_size=kernel_size, h_grid=self.h_grid, input_h_grid=self.h_grid, stride=stride, padding=padding, wscale=wscale,
                                       channel_attention=ch_GG(N_out= N_channels  , N_in=N_channels  , ratio=ch_ratio),
                                       )
        self.c3 = se2_layers.AttConvGG(N_in=N_channels  , N_out=N_channels  , kernel_size=kernel_size, h_grid=self.h_grid, input_h_grid=self.h_grid, stride=2     , padding=padding, wscale=wscale,
                                       channel_attention=ch_GG(N_out=N_channels  , N_in=N_channels  , ratio=ch_ratio),
                                       )
        self.c4 = se2_layers.AttConvGG(N_in=N_channels  , N_out=N_channels_2, kernel_size=kernel_size, h_grid=self.h_grid, input_h_grid=self.h_grid, stride=stride, padding=padding, wscale=wscale,
                                       channel_attention=ch_GG(N_out=N_channels_2, N_in=N_channels  , ratio=ch_ratio),
                                       )
        self.c5 = se2_layers.AttConvGG(N_in=N_channels_2, N_out=N_channels_2, kernel_size=kernel_size, h_grid=self.h_grid, input_h_grid=self.h_grid, stride=stride, padding=padding, wscale=wscale,
                                       channel_attention=ch_GG(N_out=N_channels_2, N_in=N_channels_2, ratio=ch_ratio),
                                       )
        self.c6 = se2_layers.AttConvGG(N_in=N_channels_2, N_out=N_channels_2, kernel_size=kernel_size, h_grid=self.h_grid, input_h_grid=self.h_grid, stride=2     , padding=padding, wscale=wscale,
                                       channel_attention=ch_GG(N_out=N_channels_2, N_in=N_channels_2, ratio=ch_ratio),
                                       )
        self.c7 = se2_layers.AttConvGG(N_in=N_channels_2, N_out=N_channels_2, kernel_size=kernel_size, h_grid=self.h_grid, input_h_grid=self.h_grid, stride=stride, padding=padding, wscale=wscale,
                                       channel_attention=ch_GG(N_out=N_channels_2, N_in=N_channels_2, ratio=ch_ratio),
                                       )
        self.c8 = se2_layers.AttConvGG(N_in=N_channels_2, N_out=N_channels_2, kernel_size=1          , h_grid=self.h_grid, input_h_grid=self.h_grid, stride=stride, padding=0      , wscale=wscale,
                                       channel_attention=ch_GG(N_out=N_channels_2, N_in=N_channels_2, ratio=ch_ratio),
                                       )
        self.c9 = se2_layers.AttConvGG(N_in=N_channels_2, N_out=10          , kernel_size=1          , h_grid=self.h_grid, input_h_grid=self.h_grid, stride=stride, padding=0      , wscale=wscale,
                                       channel_attention=ch_GG(N_out=10          , N_in=N_channels_2, ratio=ch_ratio),
                                       )
        self.dp_init = nn.Dropout(p_init)
        self.dp = nn.Dropout(p)
        self.bn1 = nn.BatchNorm3d(num_features=N_channels  , eps=eps)
        self.bn2 = nn.BatchNorm3d(num_features=N_channels  , eps=eps)
        self.bn3 = nn.BatchNorm3d(num_features=N_channels  , eps=eps)
        self.bn4 = nn.BatchNorm3d(num_features=N_channels_2, eps=eps)
        self.bn5 = nn.BatchNorm3d(num_features=N_channels_2, eps=eps)
        self.bn6 = nn.BatchNorm3d(num_features=N_channels_2, eps=eps)
        self.bn7 = nn.BatchNorm3d(num_features=N_channels_2, eps=eps)
        self.bn8 = nn.BatchNorm3d(num_features=N_channels_2, eps=eps)
        self.bn9 = nn.BatchNorm3d(num_features=10, eps=eps)
class A_Sp_P4AllCNNC(P4AllCNNC):
    def __init__(self, use_bias=False, attention=False):
        super(A_Sp_P4AllCNNC, self).__init__()
        import importlib
        group_name = 'SE2'
        group = importlib.import_module('attgconv.group.' + group_name)
        import attgconv
        se2_layers = attgconv.layers(group)  
        n_grid = 4
        self.h_grid = se2_layers.H.grid_global(n_grid)
        p_init = 0.2
        p = 0.5
        stride = 1
        padding = 1
        kernel_size = 3
        N_channels = 48 
        N_channels_2 = N_channels * 2
        eps = 2e-5
        wscale = 0.035  
        ch_ratio = 16        
        sp_kernel_size = 7
        self.ch_ratio = ch_ratio
        self.sp_kernel_size = sp_kernel_size
        from attgconv.attention_layers import ChannelAttention as ch_RnG
        from attgconv.attention_layers import ChannelAttentionGG 
        from attgconv.attention_layers import SpatialAttention 
        from attgconv.attention_layers import SpatialAttentionGG
        ch_GG = functools.partial(ChannelAttentionGG, N_h=n_grid, N_h_in=n_grid)
        sp_RnG = functools.partial(SpatialAttention, group=group, h_grid=self.h_grid, stride=stride, wscale=wscale)
        sp_GG = functools.partial(SpatialAttentionGG, group=group, h_grid=self.h_grid, input_h_grid=self.h_grid, stride=stride, wscale=wscale)
        self.c1 = se2_layers.AttConvRnG(N_in=3          , N_out=N_channels  , kernel_size=kernel_size, h_grid=self.h_grid, stride=stride, padding=padding, wscale=wscale,
                                        spatial_attention=sp_RnG(N_out=N_channels, N_in=3        , kernel_size=sp_kernel_size)
                                        )
        self.c2 = se2_layers.AttConvGG(N_in=N_channels  , N_out=N_channels  , kernel_size=kernel_size, h_grid=self.h_grid, input_h_grid=self.h_grid, stride=stride, padding=padding, wscale=wscale,
                                       spatial_attention=sp_GG(N_out= N_channels  , N_in=N_channels  , kernel_size=sp_kernel_size)
                                       )
        self.c3 = se2_layers.AttConvGG(N_in=N_channels  , N_out=N_channels  , kernel_size=kernel_size, h_grid=self.h_grid, input_h_grid=self.h_grid, stride=2     , padding=padding, wscale=wscale,
                                       spatial_attention=sp_GG(N_out=N_channels  , N_in=N_channels  , kernel_size=sp_kernel_size)
                                       )
        self.c4 = se2_layers.AttConvGG(N_in=N_channels  , N_out=N_channels_2, kernel_size=kernel_size, h_grid=self.h_grid, input_h_grid=self.h_grid, stride=stride, padding=padding, wscale=wscale,
                                       spatial_attention=sp_GG(N_out=N_channels_2, N_in=N_channels  , kernel_size=sp_kernel_size)
                                       )
        self.c5 = se2_layers.AttConvGG(N_in=N_channels_2, N_out=N_channels_2, kernel_size=kernel_size, h_grid=self.h_grid, input_h_grid=self.h_grid, stride=stride, padding=padding, wscale=wscale,
                                       spatial_attention=sp_GG(N_out=N_channels_2, N_in=N_channels_2, kernel_size=sp_kernel_size)
                                       )
        self.c6 = se2_layers.AttConvGG(N_in=N_channels_2, N_out=N_channels_2, kernel_size=kernel_size, h_grid=self.h_grid, input_h_grid=self.h_grid, stride=2     , padding=padding, wscale=wscale,
                                       spatial_attention=sp_GG(N_out=N_channels_2, N_in=N_channels_2, kernel_size=sp_kernel_size)
                                       )
        self.c7 = se2_layers.AttConvGG(N_in=N_channels_2, N_out=N_channels_2, kernel_size=kernel_size, h_grid=self.h_grid, input_h_grid=self.h_grid, stride=stride, padding=padding, wscale=wscale,
                                       spatial_attention=sp_GG(N_out=N_channels_2, N_in=N_channels_2, kernel_size=sp_kernel_size)
                                       )
        self.c8 = se2_layers.AttConvGG(N_in=N_channels_2, N_out=N_channels_2, kernel_size=1          , h_grid=self.h_grid, input_h_grid=self.h_grid, stride=stride, padding=0      , wscale=wscale,
                                       spatial_attention=sp_GG(N_out=N_channels_2, N_in=N_channels_2, kernel_size=sp_kernel_size)
                                       )
        self.c9 = se2_layers.AttConvGG(N_in=N_channels_2, N_out=10          , kernel_size=1          , h_grid=self.h_grid, input_h_grid=self.h_grid, stride=stride, padding=0      , wscale=wscale,
                                       spatial_attention=sp_GG(N_out=10          , N_in=N_channels_2, kernel_size=sp_kernel_size)
                                       )
        self.dp_init = nn.Dropout(p_init)
        self.dp = nn.Dropout(p)
        self.bn1 = nn.BatchNorm3d(num_features=N_channels  , eps=eps)
        self.bn2 = nn.BatchNorm3d(num_features=N_channels  , eps=eps)
        self.bn3 = nn.BatchNorm3d(num_features=N_channels  , eps=eps)
        self.bn4 = nn.BatchNorm3d(num_features=N_channels_2, eps=eps)
        self.bn5 = nn.BatchNorm3d(num_features=N_channels_2, eps=eps)
        self.bn6 = nn.BatchNorm3d(num_features=N_channels_2, eps=eps)
        self.bn7 = nn.BatchNorm3d(num_features=N_channels_2, eps=eps)
        self.bn8 = nn.BatchNorm3d(num_features=N_channels_2, eps=eps)
        self.bn9 = nn.BatchNorm3d(num_features=10, eps=eps)
if __name__ == '__main__':
    from experiments.utils import num_params
    model = AllCNNC()
    model(torch.rand([1, 3, 32, 32]))  
    num_params(model)
    model = P4AllCNNC()
    model(torch.rand([1, 3, 32, 32]))  
    num_params(model)
    model = fA_P4AllCNNC()
    model(torch.rand([1,3,32,32]))  
    num_params(model)
    model = P4MAllCNNC()
    model(torch.rand([1,3,32,32]))  
    num_params(model)
    model = fA_P4MAllCNNC()
    model(torch.rand([1,3,32,32]))  
    num_params(model)