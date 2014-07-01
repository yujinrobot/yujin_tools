## RosJava

```
> yujin_init_workspace ~/rosjava rosjava
> cd ~/rosjava
> yujin_init_build .
> yujin_make --install-rosdeps
> yujin_make
```

## Android

This is assuming you have the latest android studio.

```
> yujin_init_workspace ~/android_core android_core
> cd ~/android_core
> yujin_init_build --underlays=~/rosjava/devel .
> yujin_make
```

## Android Interactions


```
> yujin_init_workspace ~/rocon_rosjava rocon_rosjava
> cd ~/rocon_rosjava
> yujin_init_build --underlays="~/rosjava/devel" .
> yujin_make
```

```
> yujin_init_workspace ~/android_interactions android_interactions
> cd ~/android_interactions
> yujin_init_build --underlays="~/android_core/devel;~/rocon_rosjava/devel;~/rosjava/devel" .
> yujin_make
```

